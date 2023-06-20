from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from sso import helpers as sso_helpers


class SignUpMixin:
    def handle_400_response(self, response, form):
        server_errors = response.json()
        for attribute, value in server_errors.items():
            form.add_error(attribute, value)

    def handle_signup_success(self, response, form, redirect_url):
        user_details = response.json()
        uidb64 = user_details['uidb64']
        token = user_details['verification_token']

        sso_helpers.send_verification_code_email(
            email=form.cleaned_data['email'],
            verification_code=user_details['verification_code'],
            form_url=self.request.path,
            verification_link=self.get_verification_link(uidb64, token),
            resend_verification_link=self.get_resend_verification_link(),
        )
        return HttpResponseRedirect(reverse_lazy(redirect_url) + '?uidb64=' + uidb64 + '&token=' + token)


class VerifyCodeMixin:
    def __init__(self, code_expired_error):
        self.code_expired_error = code_expired_error

    def send_welcome_notification(self):
        pass

    def handle_code_expired(self, upstream_response, request, uidb64, token, form):
        email = upstream_response.json()['email']
        verification_code = sso_helpers.regenerate_verification_code(email)
        sso_helpers.send_verification_code_email(
            email=email,
            verification_code=verification_code,
            form_url=request.path,
            verification_link=self.get_verification_link(uidb64, token),
            resend_verification_link=self.get_resend_verification_link(),
        )
        form.add_error(self.code_expired_error['field'], self.code_expired_error['error_message'])

    def handle_verification_code_success(self, upstream_response, redirect_url):
        email = upstream_response.json()['email']
        self.send_welcome_notification(email=email, form_url=self.request.path)
        cookie_jar = sso_helpers.get_cookie_jar(upstream_response)
        response = HttpResponseRedirect(reverse_lazy(redirect_url))
        sso_helpers.set_cookies_from_cookie_jar(
            cookie_jar=cookie_jar,
            response=response,
            whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
        )
        return response
