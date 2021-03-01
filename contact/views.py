from urllib.parse import urlparse

from directory_forms_api_client.helpers import FormSessionMixin, Sender
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from contact import constants, forms as contact_forms
from core import mixins as core_mixins
from core.datastructures import NotifySettings


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
            snippet=self.get_snippet_instance(),
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
