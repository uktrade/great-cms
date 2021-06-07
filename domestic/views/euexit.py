from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from core import snippet_slugs
from core.mixins import GetSnippetContentMixin, PrepopulateFormMixin, TranslationsMixin
from domestic import forms

SESSION_KEY_FORM_INGRESS_URL = 'FORM_INGRESS_URL'


class HideLanguageSelectorMixin(TranslationsMixin):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            hide_language_selector=True,
            **kwargs,
        )


class BaseInternationalContactFormView(
    GetSnippetContentMixin,
    PrepopulateFormMixin,
    # CountryDisplayMixin,  # TODO: port from directory-components when we get a page that needs this
    HideLanguageSelectorMixin,
    FormView,
):
    page_type = 'ContactPage'

    def get(self, *args, **kwargs):
        self.request.session[SESSION_KEY_FORM_INGRESS_URL] = self.request.META.get('HTTP_REFERER')
        return super().get(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ingress_url'] = self.request.session.get(SESSION_KEY_FORM_INGRESS_URL)
        return kwargs

    def form_valid(self, form):
        sender = Sender(
            email_address=form.cleaned_data['email'],
            country_code=form.cleaned_data.get('country_name'),
        )
        response = form.save(
            subject=self.subject,
            full_name=form.full_name,
            email_address=form.cleaned_data['email'],
            service_name='eu_exit',
            subdomain=settings.EU_EXIT_ZENDESK_SUBDOMAIN,
            form_url=self.request.path,
            sender=sender,
        )
        response.raise_for_status()
        return super().form_valid(form)


class BaseContactView(
    GetSnippetContentMixin,
    HideLanguageSelectorMixin,
    TemplateView,
):
    page_type = 'ContactPage'


class DomesticContactFormView(BaseInternationalContactFormView):
    slug = snippet_slugs.EUEXIT_DOMESTIC_FORM
    form_class = forms.EUExitDomesticContactForm
    template_name = 'domestic/euexit/domestic-contact-form.html'
    success_url = reverse_lazy('domestic:brexit-contact-form-success')
    subject = 'Brexit contact form'

    def get_form_initial(self):
        if self.request.user.is_authenticated and self.request.user.company:
            return {
                'email': self.request.user.email,
                'company_name': self.request.user.company['name'],
                'postcode': self.request.user.company['postal_code'],
                'first_name': self.guess_given_name,
                'last_name': self.guess_family_name,
                'organisation_type': forms.COMPANY,
            }


class DomesticContactSuccessView(BaseContactView):
    template_name = 'domestic/euexit/domestic-contact-form-success.html'
    slug = snippet_slugs.EUEXIT_FORM_SUCCESS
