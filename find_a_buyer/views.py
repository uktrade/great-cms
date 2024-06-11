from directory_constants import urls
from directory_api_client.client import api_client
from formtools.wizard.views import SessionWizardView
from requests.exceptions import HTTPError
import sentry_sdk

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse
from django.utils.decorators import method_decorator
from .decorators import must_have_company_profile


from . import forms, helpers



class Oauth2CallbackUrlMixin:
    @property
    def redirect_uri(self):
        return self.request.build_absolute_uri(
            reverse('verify-companies-house-callback')
        )
    


class UpdateCompanyProfileOnFormWizardDoneMixin:
    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def handle_profile_update_success(self):
        return redirect('company-detail')

    @staticmethod
    def send_update_error_to_sentry(sso_user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending

        sentry_sdk.set_user(
            {'hashed_uuid': sso_user.hashed_uuid, 'user_email': sso_user.email}
        )
        sentry_sdk.set_extra('api_response', str(api_response.content))
        sentry_sdk.capture_message('Updating company profile failed')

    def done(self, *args, **kwargs):
        response = api_client.company.profile_update(
            sso_session_id=self.request.user.session_id,
            data=self.serialize_form_data()
        )
        try:
            response.raise_for_status()
        except HTTPError:
            self.send_update_error_to_sentry(
                sso_user=self.request.user,
                api_response=response
            )
            raise
        else:
            return self.handle_profile_update_success()


class CompaniesHouseOauth2View(Oauth2CallbackUrlMixin, RedirectView):

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.user.session_id)
        return helpers.CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompanyVerifyView(TemplateView):

    template_name = 'company-verify-hub.html'

    def get_context_data(self, **kwargs):
        return {
            'company': self.request.user.company,
        }
    
    @method_decorator(must_have_company_profile)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]

class CompanyAddressVerificationView(
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SUCCESS = 'success'

    form_list = (
        (ADDRESS, forms.CompanyCodeVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-address-verification-form.html',
        SUCCESS: 'company-profile-address-verification-success.html'
    }

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['sso_session_id'] = self.request.user.session_id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            company=self.request.user.company,
            **kwargs
        )
    

class SendVerificationLetterView(
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SENT = 'sent'

    form_list = (
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-form-address.html',
        SENT: 'company-profile-form-letter-sent.html',
    }
    form_labels = [
        (ADDRESS, 'Address'),
    ]
    form_serializer = staticmethod(forms.serialize_company_address_form)

    def get_context_data(self, form, **kwargs):
        address = helpers.build_company_address(self.request.user.company)
        context = super().get_context_data(
            form=form,
            form_labels=self.form_labels,
            all_cleaned_data=self.get_all_cleaned_data(),
            company_name=self.request.user.company['name'],
            company_number=self.request.user.company['number'],
            company_address=address,
            **kwargs
        )
        return context

    def handle_profile_update_success(self):
        context = {'profile_url': urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile'}
        return TemplateResponse(self.request, self.templates[self.SENT], context)

