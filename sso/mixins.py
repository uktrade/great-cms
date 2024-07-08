import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from sso import helpers as sso_helpers


class SignUpMixin:
    def handle_400_response(self, response, form):
        server_errors = response.json()
        for attribute, value in server_errors.items():
            form.add_error(attribute, value)

    def handle_signup_success(self, response, form, redirect_url, verification_link):
        user_details = response.json()

        sso_helpers.send_verification_code_email(
            email=form.cleaned_data['email'],
            verification_code=user_details['verification_code'],
            form_url=self.request.path,
            verification_link=verification_link,
            resend_verification_link=self.get_resend_verification_link(),
        )
        return HttpResponseRedirect(redirect_url)


class VerifyCodeMixin:
    def __init__(self, code_expired_error):
        self.code_expired_error = code_expired_error

    def send_welcome_notification(self):
        pass

    def handle_code_expired(self, upstream_response, request, form, verification_link):
        email = upstream_response.json()['email']
        verification_code = sso_helpers.regenerate_verification_code(email)
        sso_helpers.send_verification_code_email(
            email=email,
            verification_code=verification_code,
            form_url=request.path,
            verification_link=verification_link,
            resend_verification_link=self.get_resend_verification_link(),
        )
        form.add_error(self.code_expired_error['field'], self.code_expired_error['error_message'])

    def handle_verification_code_success(self, upstream_response, redirect_url):
        email = upstream_response.json()['email']
        self.send_welcome_notification(email=email, form_url=self.request.path)
        cookie_jar = sso_helpers.get_cookie_jar(upstream_response)
        response = HttpResponseRedirect(redirect_url)
        sso_helpers.set_cookies_from_cookie_jar(
            cookie_jar=cookie_jar,
            response=response,
            whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
        )
        return response


class ResendVerificationMixin:
    def get_verification_link(self, uidb64, token):
        verification_params = f'?uidb64={uidb64}&token={token}'
        return self.request.build_absolute_uri(reverse_lazy('international_online_offer:signup')) + verification_params

    def get_resend_verification_link(self):
        return self.request.build_absolute_uri(
            reverse_lazy('sso_profile:resend-verification', kwargs={'step': 'resend'})
        )


class SignInMixin(ResendVerificationMixin):
    def handle_post_request(
        self,
        data,
        form,
        request,
        success_url,
    ):
        upstream_response = requests.post(url=settings.SSO_PROXY_LOGIN_URL, data=data, allow_redirects=False)

        # 401 means credentials are correct, but user is unverified
        if upstream_response.status_code == 401:
            email = form.cleaned_data['email']
            verification_code = sso_helpers.regenerate_verification_code(email)
            uidb64 = verification_code.pop('user_uidb64')
            token = verification_code.pop('verification_token')
            sso_helpers.send_verification_code_email(
                email=email,
                verification_code=verification_code,
                form_url=request.path,
                verification_link=self.get_verification_link(uidb64, token),
                resend_verification_link=self.get_resend_verification_link(),
            )
            return 'Email unverified: we have re-sent you an email containing a link to verify your email address'
        elif upstream_response.status_code == 302:
            # 302 from sso indicate successful login
            cookie_jar = sso_helpers.get_cookie_jar(upstream_response)
            response = HttpResponseRedirect(success_url)
            sso_helpers.set_cookies_from_cookie_jar(
                cookie_jar=cookie_jar,
                response=response,
                whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
            )
            return response
        elif upstream_response.status_code == 200:
            # 200 from sso indicate the credentials were not correct
            return """The email or password you entered is not correct.
            If you've forgotten your password, you can reset it"""

        return None
