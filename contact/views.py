from urllib.parse import urlparse

from directory_forms_api_client.helpers import FormSessionMixin, Sender
from django.conf import settings
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from formtools.wizard.views import NamedUrlSessionWizardView

from contact import constants, forms as contact_forms, helpers
from core import mixins as core_mixins, snippet_slugs
from core.datastructures import NotifySettings


class SubmitFormOnGetMixin:
    # This is an unusual patterm, ported from V1. It is only safe as
    # long as the POST action of any view which uses it does NOT
    # update state or trigger a side effect...
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET or {}
        if data:
            kwargs['data'] = data
        return kwargs

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SendNotifyMessagesMixin:
    def send_agent_message(self, form):
        sender = Sender(
            email_address=form.cleaned_data['email'],
            country_code=None,
        )
        response = form.save(
            template_id=self.notify_settings.agent_template,
            email_address=self.notify_settings.agent_email,
            form_url=self.request.get_full_path(),
            form_session=self.form_session,
            sender=sender,
        )
        response.raise_for_status()

    def send_user_message(self, form):
        # no need to set `sender` as this is just a confirmation email.
        response = form.save(
            template_id=self.notify_settings.user_template,
            email_address=form.cleaned_data['email'],
            form_url=self.request.get_full_path(),
            form_session=self.form_session,
        )
        response.raise_for_status()

    def form_valid(self, form):
        self.send_agent_message(form)
        self.send_user_message(form)
        return super().form_valid(form)


class BaseNotifyFormView(
    FormSessionMixin,
    SendNotifyMessagesMixin,
    FormView,
):
    page_type = 'ContactPage'  # for use with GA360 tagging


class PrepopulateShortFormMixin(core_mixins.PrepopulateFormMixin):
    def get_form_initial(self):

        if self.request.user.is_authenticated and self.request.user.company:
            return {
                'email': self.request.user.email,
                'company_type': constants.LIMITED,
                'organisation_name': self.request.user.company.data['name'],
                'postcode': self.request.user.company.data['postal_code'],
                'given_name': self.guess_given_name,
                'family_name': self.guess_family_name,
            }


class BaseZendeskFormView(FormSessionMixin, FormView):
    def form_valid(self, form):
        sender = Sender(
            email_address=form.cleaned_data['email'],
            country_code=None,
        )
        response = form.save(
            email_address=form.cleaned_data['email'],
            full_name=form.full_name,
            subject=self.subject,
            service_name=settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME,
            form_url=self.request.get_full_path(),
            form_session=self.form_session,
            sender=sender,
            subdomain=self.kwargs.get('zendesk_subdomain'),
        )
        response.raise_for_status()
        return super().form_valid(form)


class BaseSuccessView(
    FormSessionMixin,
    core_mixins.GetSnippetContentMixin,
    TemplateView,
):
    def clear_form_session(self, response):
        self.form_session.clear()

    def get(self, *args, **kwargs):
        # setting ingress url not very meaningful here, so skip it.
        response = super(FormSessionMixin, self).get(*args, **kwargs)
        response.add_post_render_callback(self.clear_form_session)
        return response

    def get_next_url(self):
        # If the ingress URL is internal and it's not contact page then allow
        # user to go back to it, else send them to the homepage
        parsed_url = urlparse(self.form_session.ingress_url)
        if parsed_url.netloc == self.request.get_host() and not parsed_url.path.startswith('/contact'):
            return self.form_session.ingress_url
        return '/'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            next_url=self.get_next_url(),
        )


class DomesticFormView(PrepopulateShortFormMixin, BaseZendeskFormView):
    form_class = contact_forms.DomesticForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    subject = settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT


class DomesticEnquiriesFormView(PrepopulateShortFormMixin, BaseNotifyFormView):
    form_class = contact_forms.DomesticEnquiriesForm
    template_name = 'domestic/contact/step-enquiries.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID,
    )


class DomesticSuccessView(BaseSuccessView):
    template_name = 'domestic/contact/submit-success-domestic.html'


class EcommerceSupportFormPageView(BaseNotifyFormView):
    template_name = 'domestic/contact/request-export-support-form.html'
    form_class = contact_forms.ExportSupportForm
    success_url = reverse_lazy('contact:ecommerce-export-support-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_NOTIFY_TEMPLATE_ID,
    )


class ExportSupportSuccessPageView(TemplateView):
    template_name = 'domestic/contact/request-export-support-success.html'


class RoutingFormView(
    FormSessionMixin,
    NamedUrlSessionWizardView,
):

    # given the current step, based on selected  option, where to redirect.
    redirect_mapping = {
        constants.DOMESTIC: {
            constants.TRADE_OFFICE: reverse_lazy('contact:office-finder'),
            constants.EXPORT_ADVICE: reverse_lazy('contact:contact-us-export-advice', kwargs={'step': 'comment'}),
            constants.FINANCE: reverse_lazy(
                'domestic:uk-export-finance-lead-generation-form', kwargs={'step': 'contact'}
            ),
            constants.EUEXIT: reverse_lazy('domestic:brexit-contact-form'),
            constants.EVENTS: reverse_lazy('contact:contact-us-events-form'),
            constants.DSO: reverse_lazy('contact:contact-us-dso-form'),
            constants.OTHER: reverse_lazy('contact:contact-us-enquiries'),
        },
        # constants.INTERNATIONAL: {
        #     constants.INVESTING: settings.INVEST_CONTACT_URL,
        #     constants.CAPITAL_INVEST: settings.CAPITAL_INVEST_CONTACT_URL,
        #     constants.EXPORTING_TO_UK: helpers.build_exporting_guidance_url(slugs.HELP_EXPORTING_TO_UK),
        #     constants.BUYING: settings.FIND_A_SUPPLIER_CONTACT_URL,
        #     constants.EUEXIT: settings.EU_EXIT_INTERNATIONAL_CONTACT_URL,
        #     constants.OTHER: reverse_lazy('contact:contact-us-international'),
        # },
        # constants.EXPORT_OPPORTUNITIES: {
        #     constants.NO_RESPONSE: helpers.build_export_opportunites_guidance_url(slugs.HELP_EXOPPS_NO_RESPONSE),
        #     constants.ALERTS: helpers.build_export_opportunites_guidance_url(slugs.HELP_EXOPP_ALERTS_IRRELEVANT),
        #     constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        # },
        constants.GREAT_SERVICES: {
            constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        },
        constants.GREAT_ACCOUNT: {
            constants.NO_VERIFICATION_EMAIL: helpers.build_account_guidance_url(
                snippet_slugs.HELP_MISSING_VERIFY_EMAIL
            ),
            constants.PASSWORD_RESET: helpers.build_account_guidance_url(snippet_slugs.HELP_PASSWORD_RESET),
            constants.COMPANY_NOT_FOUND: helpers.build_account_guidance_url(
                snippet_slugs.HELP_ACCOUNT_COMPANY_NOT_FOUND
            ),
            constants.COMPANIES_HOUSE_LOGIN: helpers.build_account_guidance_url(
                snippet_slugs.HELP_COMPANIES_HOUSE_LOGIN
            ),
            constants.VERIFICATION_CODE: helpers.build_account_guidance_url(snippet_slugs.HELP_VERIFICATION_CODE_ENTER),
            constants.NO_VERIFICATION_LETTER: helpers.build_account_guidance_url(
                snippet_slugs.HELP_VERIFICATION_CODE_LETTER
            ),
            constants.NO_VERIFICATION_MISSING: helpers.build_account_guidance_url(
                snippet_slugs.HELP_VERIFICATION_CODE_MISSING
            ),
            constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        },
        # constants.EXPORTING_TO_UK: {
        #     constants.HMRC: settings.CONTACT_EXPORTING_TO_UK_HMRC_URL,
        #     constants.DEFRA: reverse_lazy('contact:contact-us-exporting-to-the-uk-defra'),
        #     constants.BEIS: reverse_lazy('contact:contact-us-exporting-to-the-uk-beis'),
        #     constants.IMPORT_CONTROLS: (reverse_lazy('contact:contact-us-international')),
        #     constants.TRADE_WITH_UK_APP: (reverse_lazy('contact:contact-us-international')),
        #     constants.OTHER: reverse_lazy('contact:contact-us-international'),
        # },
    }

    form_list = (
        (constants.LOCATION, contact_forms.LocationRoutingForm),
        (constants.DOMESTIC, contact_forms.DomesticRoutingForm),
        (constants.GREAT_SERVICES, contact_forms.GreatServicesRoutingForm),
        (constants.GREAT_ACCOUNT, contact_forms.GreatAccountRoutingForm),
        (constants.EXPORT_OPPORTUNITIES, contact_forms.ExportOpportunitiesRoutingForm),
        (constants.INTERNATIONAL, contact_forms.InternationalRoutingForm),
        # (constants.EXPORTING_TO_UK, contact_forms.ExportingIntoUKRoutingForm),
        ('NO-OPERATION', contact_forms.NoOpForm),  # should never be reached
    )
    templates = {
        constants.LOCATION: 'domestic/contact/routing/step-location.html',
        constants.DOMESTIC: 'domestic/contact/routing/step-domestic.html',
        constants.GREAT_SERVICES: 'domestic/contact/routing/step-great-services.html',
        constants.GREAT_ACCOUNT: 'domestic/contact/routing/step-great-account.html',
        # constants.EXPORT_OPPORTUNITIES: ('contact/routing/step-export-opportunities-service.html'),
        # constants.INTERNATIONAL: 'contact/routing/step-international.html',
        # constants.EXPORTING_TO_UK: 'contact/routing/step-exporting.html',
    }

    # given current step, where to send them back to
    back_mapping = {
        constants.DOMESTIC: constants.LOCATION,
        constants.INTERNATIONAL: constants.LOCATION,
        constants.GREAT_SERVICES: constants.DOMESTIC,
        constants.GREAT_ACCOUNT: constants.GREAT_SERVICES,
        constants.EXPORT_OPPORTUNITIES: constants.GREAT_SERVICES,
        constants.EXPORTING_TO_UK: constants.INTERNATIONAL,
    }

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_redirect_url(self, choice):
        if self.steps.current in self.redirect_mapping:
            mapping = self.redirect_mapping[self.steps.current]
            return mapping.get(choice)

    def render_next_step(self, form):
        self.form_session.funnel_steps.append(self.steps.current)
        choice = form.cleaned_data['choice']
        redirect_url = self.get_redirect_url(choice)
        if redirect_url:
            # clear the ingress URL when redirecting away from the service as
            # the "normal way" for clearing it via success page will not be hit
            # assumed that internal redirects will not contain domain, but be
            # relative to current site.
            if urlparse(str(redirect_url)).netloc:
                self.form_session.clear()
            return redirect(redirect_url)
        return self.render_goto_step(choice)

    def get_prev_step(self, step=None):
        if step is None:
            step = self.steps.current
        return self.back_mapping.get(step)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        parsed_url = urlparse(self.form_session.ingress_url)
        if parsed_url.netloc == self.request.get_host():
            context_data['prev_url'] = self.form_session.ingress_url
        return context_data


class GuidanceView(
    core_mixins.GetSnippetContentMixin,
    TemplateView,
):
    template_name = 'domestic/contact/guidance.html'


class OfficeFinderFormView(SubmitFormOnGetMixin, FormView):
    template_name = 'domestic/contact/office-finder.html'
    form_class = contact_forms.OfficeFinderForm
    postcode = ''

    @cached_property
    def all_offices(self):
        return helpers.retrieve_regional_offices(self.postcode)

    def form_valid(self, form):
        self.postcode = form.cleaned_data['postcode']
        office_details = helpers.extract_regional_office_details(self.all_offices)
        other_offices = helpers.extract_other_offices_details(self.all_offices)
        return TemplateResponse(
            self.request,
            self.template_name,
            {
                'office_details': office_details,
                'other_offices': other_offices,
                **self.get_context_data(),
            },
        )


class OfficeContactFormView(PrepopulateShortFormMixin, BaseNotifyFormView):
    template_name = 'domestic/contact/step.html'
    form_class = contact_forms.TradeOfficeContactForm

    @property
    def agent_email(self):
        return (
            helpers.retrieve_regional_office_email(self.kwargs['postcode'])
            or settings.CONTACT_DIT_AGENT_EMAIL_ADDRESS  # noqa: W503
        )

    @property
    def notify_settings(self):
        return NotifySettings(
            agent_template=settings.CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID,
            agent_email=self.agent_email,
            user_template=settings.CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID,
        )

    def get_success_url(self):
        return reverse(
            'contact:contact-us-office-success',
            kwargs={'postcode': self.kwargs['postcode']},
        )


class OfficeSuccessView(DomesticSuccessView):
    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'next_url': '/',
        }


class EventsFormView(PrepopulateShortFormMixin, BaseNotifyFormView):
    form_class = contact_forms.EventsForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-events-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_EVENTS_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID,
    )


class DefenceAndSecurityOrganisationFormView(PrepopulateShortFormMixin, BaseNotifyFormView):
    form_class = contact_forms.DefenceAndSecurityOrganisationForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-dso-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_DSO_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID,
    )


class FeedbackFormView(core_mixins.PrepopulateFormMixin, BaseZendeskFormView):
    form_class = contact_forms.FeedbackForm
    template_name = 'domestic/contact/comment-contact.html'
    success_url = reverse_lazy('contact:contact-us-feedback-success')
    subject = settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT

    def get_form_initial(self):
        if self.request.user.is_authenticated:
            return {
                'email': self.request.user.email,
                'name': self.request.user.get_full_name(),
            }
