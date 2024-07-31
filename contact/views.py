import pickle
from http.client import CREATED
from urllib.parse import urlparse

from directory_forms_api_client import actions
from directory_forms_api_client.helpers import FormSessionMixin, Sender
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from formtools.wizard.views import NamedUrlSessionWizardView
from rest_framework.generics import GenericAPIView

from contact import constants, forms as contact_forms, helpers, mixins as contact_mixins
from core import mixins as core_mixins, snippet_slugs
from core.cms_slugs import (
    DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
    PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE,
)
from core.datastructures import NotifySettings
from directory_constants.choices import COUNTRY_CHOICES


class BespokeBreadcrumbMixin(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['bespoke_breadcrumbs'] = [
            {'title': 'Contact us', 'url': reverse('contact:contact-us-routing-form', kwargs={'step': 'location'})},
        ]
        return ctx


class WizardBespokeBreadcrumbMixin(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if settings.FEATURE_DIGITAL_POINT_OF_ENTRY:
            bespoke_breadcrumbs = [
                {'title': 'Guidance and Support', 'url': DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE},
            ]
        else:
            bespoke_breadcrumbs = [
                {'title': 'Contact us', 'url': reverse('contact:contact-us-routing-form', kwargs={'step': 'location'})},
            ]
        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        return ctx


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


class SendNotifyUserMessageMixin:
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
        self.send_user_message(form)
        return super().form_valid(form)


class SendNotifyMessagesMixin(SendNotifyUserMessageMixin):
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

    def form_valid(self, form):
        self.send_agent_message(form)
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


class BaseNotifyUserFormView(
    FormSessionMixin,
    SendNotifyUserMessageMixin,
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


class DomesticFormView(WizardBespokeBreadcrumbMixin, PrepopulateShortFormMixin, BaseZendeskFormView):
    form_class = contact_forms.DomesticForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    subject = settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT


class DomesticEnquiriesFormView(WizardBespokeBreadcrumbMixin, PrepopulateShortFormMixin, BaseNotifyFormView):
    form_class = contact_forms.DomesticEnquiriesForm
    template_name = 'domestic/contact/step-enquiries.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID,
    )


class DomesticSuccessView(BespokeBreadcrumbMixin, BaseSuccessView):
    template_name = 'domestic/contact/submit-success-domestic.html'


class DomesticExportSupportFormStep1View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep1Form
    template_name = 'domestic/contact/export-support/step-1.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            heading_text='Ask our export support team a question',
            step_text='Step 1 of 6',
        )

    def get_success_url(self):
        business_type = self.request.POST.get('business_type')
        url_map = {
            'other': 'contact:export-support-step-2b-edit',
            'soletrader': 'contact:export-support-step-2c-edit',
        }

        if self.kwargs.get('edit'):
            if self.has_business_type_changed:
                return reverse_lazy(
                    url_map.get(business_type) if url_map.get(business_type) else 'contact:export-support-step-2a-edit'
                )
            else:
                return reverse_lazy('contact:export-support-step-7')
        else:
            if business_type == 'other':
                return reverse_lazy('contact:export-support-step-2b')
            elif business_type == 'soletrader':
                return reverse_lazy('contact:export-support-step-2c')
            else:
                return reverse_lazy('contact:export-support-step-2a')

    def form_valid(self, form):
        form_data = {}

        if self.request.session.get('form_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0]
            self.has_business_type_changed = form_data.get('business_type') != self.request.POST.get('business_type')

        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep2AView(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep2AForm
    template_name = 'domestic/contact/export-support/step-2.html'

    def get_context_data(self, **kwargs):
        back_link = reverse_lazy('contact:export-support')

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About your business',
            step_text='Step 2 of 6',
            back_link=back_link,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-3')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep2BView(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep2BForm
    template_name = 'domestic/contact/export-support/step-2.html'

    def get_context_data(self, **kwargs):
        back_link = reverse_lazy('contact:export-support')

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About your business',
            step_text='Step 2 of 6',
            back_link=back_link,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-3')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep2CView(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep2CForm
    template_name = 'domestic/contact/export-support/step-2.html'

    def get_context_data(self, **kwargs):
        back_link = reverse_lazy('contact:export-support')

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About your business',
            step_text='Step 2 of 6',
            back_link=back_link,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-3')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep3View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep3Form
    template_name = 'domestic/contact/export-support/step-3.html'
    success_url = reverse_lazy('contact:export-support-step-4')

    def get_context_data(self, **kwargs):
        form_data = {}
        business_type = self.request.POST.get('business_type')
        url_map = {
            'other': 'contact:export-support-step-2b',
            'soletrader': 'contact:export-support-step-2c',
        }
        back_link = reverse_lazy(
            url_map.get(business_type) if url_map.get(business_type) else 'contact:export-support-step-2a'
        )

        if self.request.session.get('form_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0]

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About you',
            strapline_text='This information will allow us to contact you about your enquiry.',
            step_text='Step 3 of 6',
            form_data=form_data,
            back_link=back_link,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-4')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep4View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep4Form
    template_name = 'domestic/contact/export-support/step-4.html'
    success_url = reverse_lazy('contact:export-support-step-5')

    def get_context_data(self, **kwargs):
        back_link = reverse_lazy('contact:export-support-step-3')

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About your product or service',
            strapline_text="""This information will help us provide support for your specific product or service.
             Try to keep your descriptions short (2-3 words) and use the link to add up to 5 products or services.""",
            step_text='Step 4 of 6',
            back_link=back_link,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-5')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep5View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep5Form
    template_name = 'domestic/contact/export-support/step-5.html'

    def get_context_data(self, **kwargs):
        form_data = {}
        back_link = reverse_lazy('contact:export-support-step-4')

        if self.request.session.get('form_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0]

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        return super().get_context_data(
            **kwargs,
            heading_text='About your export markets',
            strapline_text='This information will help us provide support for your specific product or service.',
            step_text='Step 5 of 6',
            back_link=back_link,
            form_data=form_data,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('contact:export-support-step-7')
        else:
            return reverse_lazy('contact:export-support-step-6')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep6View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep6Form
    template_name = 'domestic/contact/export-support/step-6.html'
    success_url = reverse_lazy('contact:export-support-step-7')

    def get_context_data(self, **kwargs):
        countries_mapping = dict(COUNTRY_CHOICES + [('notspecificcountry', '')])
        form_data = {}
        markets = []
        back_link = reverse_lazy('contact:export-support-step-5')

        if self.kwargs.get('edit'):
            back_link = reverse_lazy('contact:export-support-step-7')

        if self.request.session.get('form_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0]

        if form_data.get('markets'):
            markets = [countries_mapping[market] for market in form_data.get('markets') if countries_mapping[market]]

        return super().get_context_data(
            **kwargs,
            heading_text='About your enquiry',
            strapline_text='This information will help us direct you to the right support for your business.',
            step_text='Step 6 of 6',
            markets=markets,
            products_and_services=[
                product_or_service
                for product_or_service in [
                    form_data.get('product_or_service_1'),
                    form_data.get('product_or_service_2'),
                    form_data.get('product_or_service_3'),
                    form_data.get('product_or_service_4'),
                    form_data.get('product_or_service_5'),
                ]
                if product_or_service
            ],
            business_name=form_data.get('business_name'),
            back_link=back_link,
        )

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep7View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep7Form
    template_name = 'domestic/contact/export-support/cya.html'
    success_url = reverse_lazy('contact:export-support-step-8')

    def submit_enquiry(self, form):
        cleaned_data = form.cleaned_data

        form_data = {**self.initial_data, **cleaned_data}

        form_with_custom_fields = helpers.populate_custom_fields(form_data)

        human_readable_form_data = helpers.dpe_clean_submission_for_zendesk(form_with_custom_fields)

        sender = Sender(
            email_address=form_data.get('email'),
            country_code=None,
        )

        action = actions.ZendeskAction(
            full_name=f"{form_data.get('first_name')} {form_data.get('last_name')}",
            email_address=form_data.get('email'),
            subject=f"{form_data.get('product_or_service_1')}",
            service_name='great',
            subdomain=settings.EU_EXIT_ZENDESK_SUBDOMAIN,
            form_url=self.request.get_full_path(),
            sender=sender,
            sort_fields_alphabetically=False,
        )

        response = action.save(human_readable_form_data)
        response.raise_for_status()

    def get_context_data(self, **kwargs):
        form_data = {}
        second_step_edit_page = 'contact:export-support-step-2a-edit'
        url_map = {
            'other': 'contact:export-support-step-2b-edit',
            'soletrader': 'contact:export-support-step-2c-edit',
        }
        markets = []

        if self.request.session.get('form_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0]
            business_type = form_data.get('business_type')
            second_step_edit_page = reverse_lazy(
                url_map.get(business_type) if url_map.get(business_type) else second_step_edit_page
            )
            markets = form_data.get('markets')

        return super().get_context_data(
            **kwargs,
            heading_text='Check your answers',
            strapline_text="Check the information you've provided before you submit your enquiry.",
            steps=helpers.get_steps(form_data, second_step_edit_page, markets),
            back_link=reverse_lazy('contact:export-support-step-5'),
        )

    def form_valid(self, form):
        self.save_data(form)
        self.submit_enquiry(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep8View(contact_mixins.ExportSupportFormMixin, FormView):
    form_class = contact_forms.DomesticExportSupportStep8Form
    template_name = 'domestic/contact/export-support/confirmation.html'
    success_url = reverse_lazy('contact:export-support-step-9')
    subject = 'DPE Feedback form'

    def submit_feedback(self, form):
        cleaned_data = form.cleaned_data
        form_data = {**self.initial_data, **cleaned_data}

        sender = Sender(
            email_address=form_data.get('email'),
            country_code=None,
        )

        action = actions.SaveOnlyInDatabaseAction(
            full_name=f"{form_data.get('first_name')} {form_data.get('last_name')}",
            email_address=form_data.get('email'),
            subject=self.subject,
            sender=sender,
            form_url=self.request.get_full_path(),
        )

        response = action.save(cleaned_data)
        response.raise_for_status()

    def get_office_details(self):
        postcode = ''

        if self.request.session.get('form_data'):
            postcode = pickle.loads(bytes.fromhex(self.request.session.get('form_data')))[0].get('business_postcode')
            regional_offices = helpers.retrieve_regional_offices(postcode)

        return (
            helpers.extract_regional_office_details(regional_offices) if self.request.session.get('form_data') else None
        )

    def get_context_data(self, **kwargs):
        office_details = self.get_office_details()
        is_feedback_form = True
        show_regional_office = False

        return super().get_context_data(
            **kwargs,
            heading_text='Thank you for your enquiry',
            strapline_text="We've sent a confirmation email to the email address you provided.",
            is_feedback_form=is_feedback_form,
            office_details=office_details,
            show_regional_office=show_regional_office,
        )

    def form_valid(self, form):
        self.submit_feedback(form)
        return super().form_valid(form)


class DomesticExportSupportFormStep9View(TemplateView):
    template_name = 'domestic/contact/export-support/feedback-confirmation.html'


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

    def get_context_data(self, **kwargs):
        bespoke_breadcrumbs = [
            {
                'title': 'Contact us',
                'url': reverse(
                    'contact:contact-us-routing-form',
                    kwargs={'step': 'location'},
                ),
            },
        ]
        return super().get_context_data(bespoke_breadcrumbs=bespoke_breadcrumbs, **kwargs)


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
    BespokeBreadcrumbMixin,
    core_mixins.GetSnippetContentMixin,
    TemplateView,
):
    template_name = 'domestic/contact/guidance.html'


class OfficeFinderFormView(BespokeBreadcrumbMixin, SubmitFormOnGetMixin, FormView):
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


class OfficeContactFormView(WizardBespokeBreadcrumbMixin, PrepopulateShortFormMixin, BaseNotifyFormView):
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


class EventsFormView(WizardBespokeBreadcrumbMixin, PrepopulateShortFormMixin, BaseNotifyFormView):
    form_class = contact_forms.EventsForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-events-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_EVENTS_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID,
    )


class DefenceAndSecurityOrganisationFormView(
    WizardBespokeBreadcrumbMixin, PrepopulateShortFormMixin, BaseNotifyFormView
):
    form_class = contact_forms.DefenceAndSecurityOrganisationForm
    template_name = 'domestic/contact/step.html'
    success_url = reverse_lazy('contact:contact-us-dso-success')
    notify_settings = NotifySettings(
        agent_template=settings.CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.CONTACT_DSO_AGENT_EMAIL_ADDRESS,
        user_template=settings.CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID,
    )


class FeedbackFormView(WizardBespokeBreadcrumbMixin, core_mixins.PrepopulateFormMixin, BaseZendeskFormView):
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


class FTASubscribeFormView(
    BaseNotifyUserFormView,
):
    form_class = contact_forms.FTASubscribeForm
    template_name = 'domestic/contact/free-trade-agreement.html'
    success_url = reverse_lazy('contact:contact-free-trade-agreements-success')
    notify_settings = NotifySettings(
        user_template=settings.SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs,
        )
        context['privacy_url'] = PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE
        return context


class InlineFeedbackView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        js_enabled = 'js_enabled' in request.query_params.keys()
        data = self.request.data.copy()
        is_human_submission = 'csrfmiddlewaretoken' not in data

        # non-js for initial yes/no form where we use query params to pass the page_useful value
        if not js_enabled and 'page_useful' in request.query_params.keys():
            data['page_useful'] = request.query_params['page_useful']
            is_human_submission = True

        email_address = request.user.email if request.user.is_authenticated else 'blank@example.com'

        sender = Sender(
            email_address=email_address,
            country_code=None,
        )

        if is_human_submission:
            action = actions.SaveOnlyInDatabaseAction(
                full_name='NA',
                email_address=email_address,
                subject='NA',
                sender=sender,
                form_url=self.request.get_full_path(),
            )

            save_result = action.save(data)

        if js_enabled:
            response = HttpResponse()
            response.status_code = save_result.status_code
            return response
        else:
            # for non-js the user is redirected to the current page with some additional QS params that are used
            # when determining which elements should be displayed and navigates the user back to #inline-feedback
            if save_result.status_code == CREATED:
                qs = (
                    f"?page_useful={data['page_useful']}"
                    if 'page_useful' in request.query_params.keys()
                    else '?detailed_feedback_submitted=True'
                )
                response = HttpResponseRedirect(redirect_to=f"{data['current_url']}{qs}/#inline-feedback")
            else:
                response = HttpResponseRedirect(
                    redirect_to=f"{data['current_url']}?submission_error=True/#inline-feedback"
                )

            response.status_code = 303
            return response
