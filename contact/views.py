from urllib.parse import urlparse

from directory_forms_api_client import actions
from directory_forms_api_client.helpers import FormSessionMixin, Sender
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from formtools.wizard.views import NamedUrlSessionWizardView

from contact import constants, forms as contact_forms, helpers
from core import mixins as core_mixins, snippet_slugs
from core.datastructures import NotifySettings
from directory_constants import urls
from sso.helpers import update_user_profile

SESSION_KEY_SOO_MARKET = 'SESSION_KEY_SOO_MARKET'
SOO_SUBMISSION_CACHE_TIMEOUT = 2592000  # 30 days


class PrepopulateInternationalFormMixin:
    # NB must be used with core_mixins.PrepopulateFormMixin
    # to have guess_given_name and guess_family_name

    def get_form_initial(self):

        if self.request.user.is_authenticated and self.request.user.company:
            return {
                'email': self.request.user.email,
                'organisation_name': getattr(self.request.user.company, 'name', ''),
                'country_name': getattr(self.request.user.company, 'country', ''),
                'city': getattr(self.request.user.company, 'locality', ''),
                'given_name': self.guess_given_name,
                'family_name': self.guess_family_name,
            }


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


class InternationalFormView(
    core_mixins.PrepopulateFormMixin,
    PrepopulateInternationalFormMixin,
    BaseNotifyFormView,
):
    form_class = contact_forms.InternationalContactForm
    template_name = 'domestic/contact/international/step.html'
    success_url = reverse_lazy('contact:contact-us-international-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID,
    )


class InternationalSuccessView(
    # CountryDisplayMixin,  # Omitted in migration as appears to be redundant..
    BaseSuccessView,
):
    template_name = 'domestic/contact/submit-success-international.html'


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
            constants.EXPORT_ADVICE: reverse_lazy(
                'contact:contact-us-export-advice',
                kwargs={'step': 'comment'},
            ),
            constants.FINANCE: reverse_lazy(
                'domestic:uk-export-finance-lead-generation-form',
                kwargs={'step': 'contact'},
            ),
            # This next one no longer exists as a view in the codebase, but can be
            # (and is) redirected at the Wagtail CMS level to a different service.
            constants.EUEXIT: '/transition-period/contact/',
            constants.EVENTS: reverse_lazy('contact:contact-us-events-form'),
            constants.DSO: reverse_lazy('contact:contact-us-dso-form'),
            constants.OTHER: reverse_lazy('contact:contact-us-enquiries'),
        },
        # V1/great-domestic-ui used to serve the International contact forms at some point
        # but then stopped when great-international-ui started handling them instead.
        # So, when this view was ported to V2, the options for constants.INTERNATIONAL
        # were deliberately left out, because they were not being used. Specifically,
        # the LocationRoutingForm sends users to /contact/triage/international if
        # 'Outside the UK' is selected which is then redirected to /international/contact/
        # via url_redirects.py
        constants.EXPORT_OPPORTUNITIES: {
            constants.NO_RESPONSE: helpers.build_export_opportunites_guidance_url(
                snippet_slugs.HELP_EXOPPS_NO_RESPONSE,
            ),
            constants.ALERTS: helpers.build_export_opportunites_guidance_url(
                snippet_slugs.HELP_EXOPP_ALERTS_IRRELEVANT,
            ),
            constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        },
        constants.GREAT_SERVICES: {
            constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        },
        constants.GREAT_ACCOUNT: {
            constants.NO_VERIFICATION_EMAIL: helpers.build_account_guidance_url(
                snippet_slugs.HELP_MISSING_VERIFY_EMAIL
            ),
            constants.PASSWORD_RESET: helpers.build_account_guidance_url(
                snippet_slugs.HELP_PASSWORD_RESET,
            ),
            constants.COMPANY_NOT_FOUND: helpers.build_account_guidance_url(
                snippet_slugs.HELP_ACCOUNT_COMPANY_NOT_FOUND
            ),
            constants.COMPANIES_HOUSE_LOGIN: helpers.build_account_guidance_url(
                snippet_slugs.HELP_COMPANIES_HOUSE_LOGIN
            ),
            constants.VERIFICATION_CODE: helpers.build_account_guidance_url(
                snippet_slugs.HELP_VERIFICATION_CODE_ENTER,
            ),
            constants.NO_VERIFICATION_LETTER: helpers.build_account_guidance_url(
                snippet_slugs.HELP_VERIFICATION_CODE_LETTER
            ),
            constants.NO_VERIFICATION_MISSING: helpers.build_account_guidance_url(
                snippet_slugs.HELP_VERIFICATION_CODE_MISSING
            ),
            constants.OTHER: reverse_lazy('contact:contact-us-domestic'),
        },
        # Similarly, constants.EXPORTING_TO_UK was the international triage config,
        # so this was not ported over
    }

    form_list = (
        (constants.LOCATION, contact_forms.LocationRoutingForm),
        (constants.DOMESTIC, contact_forms.DomesticRoutingForm),
        (constants.GREAT_SERVICES, contact_forms.GreatServicesRoutingForm),
        (constants.GREAT_ACCOUNT, contact_forms.GreatAccountRoutingForm),
        (constants.EXPORT_OPPORTUNITIES, contact_forms.ExportOpportunitiesRoutingForm),
        ('NO-OPERATION', contact_forms.NoOpForm),  # should never be reached
    )
    templates = {
        constants.LOCATION: 'domestic/contact/routing/step-location.html',
        constants.DOMESTIC: 'domestic/contact/routing/step-domestic.html',
        constants.GREAT_SERVICES: 'domestic/contact/routing/step-great-services.html',
        constants.GREAT_ACCOUNT: 'domestic/contact/routing/step-great-account.html',
        constants.EXPORT_OPPORTUNITIES: 'domestic/contact/routing/step-export-opportunities-service.html',
    }

    # given current step, where to send them back to
    back_mapping = {
        constants.DOMESTIC: constants.LOCATION,
        constants.GREAT_SERVICES: constants.DOMESTIC,
        constants.GREAT_ACCOUNT: constants.GREAT_SERVICES,
        constants.EXPORT_OPPORTUNITIES: constants.GREAT_SERVICES,
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


class ExportingAdviceFormView(
    core_mixins.PreventCaptchaRevalidationMixin,
    FormSessionMixin,
    core_mixins.PrepopulateFormMixin,
    NamedUrlSessionWizardView,
):
    success_url = reverse_lazy('contact:contact-us-domestic-success')

    COMMENT = 'comment'
    PERSONAL = 'personal'
    BUSINESS = 'business'

    form_list = (
        (COMMENT, contact_forms.CommentForm),
        (PERSONAL, contact_forms.PersonalDetailsForm),
        (BUSINESS, contact_forms.BusinessDetailsForm),
    )

    templates = {
        COMMENT: 'domestic/contact/exporting/step-comment.html',
        PERSONAL: 'domestic/contact/exporting/step-personal.html',
        BUSINESS: 'domestic/contact/exporting/step-business.html',
    }

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_kwargs(self, *args, **kwargs):
        # skipping `PrepopulateFormMixin.get_form_kwargs`
        return super(core_mixins.PrepopulateFormMixin, self).get_form_kwargs(*args, **kwargs)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if self.request.user.is_authenticated and self.request.user.company:
            if step == self.PERSONAL:
                initial.update(
                    {
                        'email': self.request.user.email,
                        'phone': getattr(
                            self.request.user.company,
                            'mobile_number',
                            '',
                        ),
                        'first_name': self.guess_given_name,
                        'last_name': self.guess_family_name,
                    }
                )
            elif step == self.BUSINESS:
                sectors = getattr(self.request.user.company, 'sectors', '')
                initial.update(
                    {
                        'company_type': constants.LIMITED,
                        'companies_house_number': getattr(self.request.user.company, 'number', ''),
                        'organisation_name': getattr(self.request.user.company, 'name', ''),
                        'postcode': getattr(self.request.user.company, 'postal_code', ''),
                        'industry': sectors[0] if sectors else None,
                        'employees': getattr(self.request.user.company, 'employees', ''),
                    }
                )
        return initial

    def send_user_message(self, form_data):
        action = actions.GovNotifyEmailAction(
            template_id=settings.CONTACT_EXPORTING_USER_NOTIFY_TEMPLATE_ID,
            email_address=form_data['email'],
            form_url=reverse('contact:contact-us-export-advice', kwargs={'step': 'comment'}),
            form_session=self.form_session,
            email_reply_to_id=settings.CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID,
        )
        response = action.save(form_data)
        response.raise_for_status()

    def send_agent_message(self, form_data):
        sender = Sender(email_address=form_data['email'], country_code=None)
        action = actions.EmailAction(
            recipients=[form_data['region_office_email']],
            subject=settings.CONTACT_EXPORTING_AGENT_SUBJECT,
            reply_to=[settings.DEFAULT_FROM_EMAIL],  # NB: this default does not appear to be used
            form_url=reverse('contact:contact-us-export-advice', kwargs={'step': 'comment'}),
            form_session=self.form_session,
            sender=sender,
        )
        template_name = 'domestic/contact/exporting-from-uk-agent-email.html'
        html = render_to_string(template_name, {'form_data': form_data})
        response = action.save({'text_body': strip_tags(html), 'html_body': html})
        response.raise_for_status()

    def done(self, form_list, **kwargs):
        form_data = self.serialize_form_list(form_list)
        self.send_agent_message(form_data)
        self.send_user_message(form_data)
        return redirect(self.success_url)

    @staticmethod
    def get_agent_email(postcode):
        region_email = helpers.retrieve_regional_office_email(postcode)
        return region_email or settings.CONTACT_DIT_AGENT_EMAIL_ADDRESS

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        data['region_office_email'] = self.get_agent_email(data['postcode'])
        return data


class SellingOnlineOverseasFormView(
    FormSessionMixin,
    core_mixins.PrepopulateFormMixin,
    NamedUrlSessionWizardView,
):
    success_url = reverse_lazy('contact:contact-us-selling-online-overseas-success')
    CONTACT_DETAILS = 'contact-details'
    APPLICANT = 'applicant'
    APPLICANT_DETAILS = 'applicant-details'
    EXPERIENCE = 'your-experience'

    form_list = (
        (CONTACT_DETAILS, contact_forms.SellingOnlineOverseasContactDetails),
        (APPLICANT, contact_forms.SellingOnlineOverseasApplicantProxy),
        (APPLICANT_DETAILS, contact_forms.SellingOnlineOverseasApplicantDetails),
        (EXPERIENCE, contact_forms.SellingOnlineOverseasExperience),
    )

    templates = {
        CONTACT_DETAILS: 'domestic/contact/soo/step-contact-details.html',
        APPLICANT: 'domestic/contact/soo/step-applicant.html',
        APPLICANT_DETAILS: 'domestic/contact/soo/step-applicant-details.html',
        EXPERIENCE: 'domestic/contact/soo/step-experience.html',
    }

    def get(self, *args, **kwargs):
        market = self.request.GET.get('market')
        if market:
            self.request.session[SESSION_KEY_SOO_MARKET] = market
        return super().get(*args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_kwargs(self, step):
        # skipping `PrepopulateFormMixin.get_form_kwargs` - legacy reason for this is unclear
        form_kwargs = super(core_mixins.PrepopulateFormMixin, self).get_form_kwargs(step)
        if step == self.APPLICANT:
            form_kwargs['company_type'] = self.request.user.company_type
        return form_kwargs

    def get_cache_prefix(self):
        return f'selling_online_overseas_form_view_{self.request.user.id}'

    def get_form_data_cache(self):
        # Note: this _looks_ like dead code – can't see a reference in an superclasses
        # See 550de82 and then e74d335 in great-domestic-ui.
        return cache.get(self.get_cache_prefix(), None)

    def set_form_data_cache(self, form_data):
        # This code is called, but because self.get_form_data_cache() doesn't appear to
        # be used, it's effectively redundant.
        cache.set(
            self.get_cache_prefix(),
            form_data,
            SOO_SUBMISSION_CACHE_TIMEOUT,
        )

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == self.CONTACT_DETAILS:
            initial.update(
                {
                    'contact_first_name': self.request.user.first_name,
                    'contact_last_name': self.request.user.last_name,
                    'contact_email': self.request.user.email,
                    'phone': self.request.user.get_mobile_number(),
                }
            )
        elif step == self.APPLICANT:
            if self.request.user.company:
                address_1 = getattr(self.request.user.company, 'address_line_1', '')
                address_2 = getattr(self.request.user.company, 'address_line_2', '')
                address = ', '.join(filter(None, [address_1, address_2]))
                initial.update(
                    {
                        'company_name': getattr(self.request.user.company, 'name', ''),
                        'company_address': address,
                        'website_address': getattr(self.request.user.company, 'website', ''),
                    }
                )
                _company_number = getattr(self.request.user.company, 'number', '')
                if _company_number:
                    initial.update(
                        {
                            'company_number': _company_number,
                        }
                    )
        elif step == self.EXPERIENCE:
            if self.request.user.company:
                initial['description'] = getattr(self.request.user.company, 'summary', '')

        return initial

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        data['market'] = self.request.session.get(SESSION_KEY_SOO_MARKET)
        return data

    def get_context_data(self, form, **kwargs):
        return {
            'market_name': self.request.session.get(SESSION_KEY_SOO_MARKET),
            **super().get_context_data(form, **kwargs),
        }

    def done(self, form_list, **kwargs):
        form_data = self.serialize_form_list(form_list)
        sender = Sender(
            email_address=form_data['contact_email'],
            country_code=None,
        )
        full_name = ('%s %s' % (form_data['contact_first_name'], form_data['contact_last_name'])).strip()
        action = actions.ZendeskAction(
            subject=settings.CONTACT_SOO_ZENDESK_SUBJECT,
            full_name=full_name,
            email_address=form_data['contact_email'],
            service_name='soo',
            form_url=reverse('contact:contact-us-soo', kwargs={'step': 'contact-details'}),
            form_session=self.form_session,
            sender=sender,
        )
        response = action.save(form_data)
        response.raise_for_status()
        user_profile_data = {'first_name': form_data['contact_first_name'], 'last_name': form_data['contact_last_name']}
        # update details in directory-sso
        update_user_profile(sso_session_id=self.request.user.session_id, data=user_profile_data)

        self.request.session.pop(SESSION_KEY_SOO_MARKET, None)
        self.set_form_data_cache(form_data)
        return redirect(self.success_url)


class SellingOnlineOverseasSuccessView(DomesticSuccessView):
    def get_next_url(self):
        return urls.domestic.SELLING_OVERSEAS

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            next_url_text='Go back to Selling Online Overseas',
        )
