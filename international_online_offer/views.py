import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from directory_sso_api_client import sso_api_client
from international_online_offer import forms
from international_online_offer.core import constants, helpers, scorecard
from international_online_offer.models import (
    TriageData,
    UserData,
    get_triage_data,
    get_triage_data_from_db_or_session,
    get_user_data,
    get_user_data_from_db_or_session,
)
from sso import helpers as sso_helpers


def calculate_and_store_is_high_value(request):
    existing_triage_data = get_triage_data_from_db_or_session(request)
    is_high_value = scorecard.score_is_high_value(
        existing_triage_data.sector,
        existing_triage_data.location,
        existing_triage_data.hiring,
        existing_triage_data.spend,
        existing_triage_data.spend_other,
    )
    if request.user.is_authenticated:
        TriageData.objects.update_or_create(
            hashed_uuid=request.user.hashed_uuid, defaults={'is_high_value': is_high_value}
        )
    else:
        request.session['is_high_value'] = is_high_value


class IOOIndex(TemplateView):
    template_name = 'ioo/index.html'


class IOOSector(FormView):
    form_class = forms.SectorForm
    template_name = 'ioo/triage/sector.html'

    def get_back_url(self):
        back_url = 'international_online_offer:index'
        if self.request.GET.get('next'):
            back_url = 'international_online_offer:' + self.request.GET.get('next')
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:intent')
        if self.request.GET.get('next'):
            next_url = reverse_lazy('international_online_offer:' + self.request.GET.get('next'))
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 1 of 5',
            question_text='What is your business sector?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your sector and products or services.""",
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'sector': triage_data.sector}

        return {'sector': self.request.session.get('sector')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'sector': form.cleaned_data['sector'],
                },
            )
        else:
            self.request.session['sector'] = form.cleaned_data['sector']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IOOIntent(FormView):
    form_class = forms.IntentForm
    template_name = 'ioo/triage/intent.html'

    def get_back_url(self):
        back_url = 'international_online_offer:sector'
        if self.request.GET.get('next'):
            back_url = 'international_online_offer:' + self.request.GET.get('next')
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:location')
        if self.request.GET.get('next'):
            next_url = reverse_lazy('international_online_offer:' + self.request.GET.get('next'))
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 2 of 5',
            question_text='How do you plan to expand your business in the UK?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your expansion plans.""",
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'intent': triage_data.intent, 'intent_other': triage_data.intent_other}

        return {'intent': self.request.session.get('intent'), 'intent_other': self.request.session.get('intent_other')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'intent': form.cleaned_data['intent'],
                    'intent_other': form.cleaned_data['intent_other'],
                },
            )
        else:
            self.request.session['intent'] = form.cleaned_data['intent']
            self.request.session['intent_other'] = form.cleaned_data['intent_other']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IOOLocation(FormView):
    form_class = forms.LocationForm
    template_name = 'ioo/triage/location.html'

    def get_back_url(self):
        back_url = 'international_online_offer:intent'
        if self.request.GET.get('next'):
            back_url = 'international_online_offer:' + self.request.GET.get('next')
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:hiring')
        if self.request.GET.get('next'):
            next_url = reverse_lazy('international_online_offer:' + self.request.GET.get('next'))
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 3 of 5',
            question_text='Where in the UK would you like to expand your business?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your city, county or region.""",
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'location': triage_data.location, 'location_none': triage_data.location_none}

        return {
            'location': self.request.session.get('location'),
            'location_none': self.request.session.get('location_none'),
        }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'location': form.cleaned_data['location'],
                    'location_none': form.cleaned_data['location_none'],
                },
            )
        else:
            self.request.session['location'] = form.cleaned_data['location']
            self.request.session['location_none'] = form.cleaned_data['location_none']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IOOHiring(FormView):
    form_class = forms.HiringForm
    template_name = 'ioo/triage/hiring.html'

    def get_back_url(self):
        back_url = 'international_online_offer:location'
        if self.request.GET.get('next'):
            back_url = 'international_online_offer:' + self.request.GET.get('next')
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:spend')
        if self.request.GET.get('next'):
            next_url = reverse_lazy('international_online_offer:' + self.request.GET.get('next'))
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 4 of 5',
            question_text='How many people are you looking to hire in the UK?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your hiring.""",
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'hiring': triage_data.hiring}

        return {'hiring': self.request.session.get('hiring')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'hiring': form.cleaned_data['hiring'],
                },
            )
        else:
            self.request.session['hiring'] = form.cleaned_data['hiring']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IOOSpend(FormView):
    form_class = forms.SpendForm
    template_name = 'ioo/triage/spend.html'

    def get_back_url(self):
        back_url = 'international_online_offer:hiring'
        if self.request.GET.get('next'):
            back_url = 'international_online_offer:' + self.request.GET.get('next')
        return back_url

    def get_success_url(self):
        next_url = '/international/expand-your-business-in-the-uk/guide/'
        if self.request.GET.get('next'):
            next_url = reverse_lazy('international_online_offer:' + self.request.GET.get('next'))
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 5 of 5',
            question_text='What is your planned spend for UK entry or expansion?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your spend.""",
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'spend': triage_data.spend, 'spend_other': triage_data.spend_other}

        return {'spend': self.request.session.get('spend'), 'spend_other': self.request.session.get('spend_other')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'spend': form.cleaned_data['spend'],
                    'spend_other': form.cleaned_data['spend_other'],
                },
            )
        else:
            self.request.session['spend'] = form.cleaned_data['spend']
            self.request.session['spend_other'] = form.cleaned_data['spend_other']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IOOProfile(FormView):
    form_class = forms.ProfileForm
    template_name = 'ioo/profile.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            complete_contact_form_message=constants.LOW_VALUE_INVESTOR_SIGNUP_MESSAGE,
            back_url='/international/expand-your-business-in-the-uk/guide/',
        )

    def get_initial(self):
        email = self.request.session.get('email')
        agree_terms = self.request.session.get('agree_terms')
        if self.request.user.is_authenticated:
            user_data = get_user_data(self.request.user.hashed_uuid)
            email = self.request.user.email
            # agreed terms if signed up already
            agree_terms = True
            if user_data:
                return {
                    'company_name': user_data.company_name,
                    'company_location': user_data.company_location,
                    'full_name': user_data.full_name,
                    'role': user_data.role,
                    'email': email,
                    'telephone_number': user_data.telephone_number,
                    'agree_terms': agree_terms,
                    'agree_info_email': user_data.agree_info_email,
                    'agree_info_telephone': user_data.agree_info_telephone,
                }

        return {
            'company_name': self.request.session.get('company_name'),
            'company_location': self.request.session.get('company_location'),
            'full_name': self.request.session.get('full_name'),
            'role': self.request.session.get('role'),
            'email': email,
            'telephone_number': self.request.session.get('telephone_number'),
            'agree_terms': agree_terms,
            'agree_info_email': self.request.session.get('agree_info_email'),
            'agree_info_telephone': self.request.session.get('agree_info_telephone'),
        }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults=form.cleaned_data,
            )
        else:
            self.request.session['company_name'] = form.cleaned_data['company_name']
            self.request.session['company_location'] = form.cleaned_data['company_location']
            self.request.session['full_name'] = form.cleaned_data['full_name']
            self.request.session['role'] = form.cleaned_data['role']
            self.request.session['email'] = form.cleaned_data['email']
            self.request.session['telephone_number'] = form.cleaned_data['telephone_number']
            self.request.session['agree_terms'] = form.cleaned_data['agree_terms']
            self.request.session['agree_info_email'] = form.cleaned_data['agree_info_email']
            self.request.session['agree_info_telephone'] = form.cleaned_data['agree_info_telephone']
        return super().form_valid(form)


class ResendVerificationMixin:
    def get_verification_link(self, uidb64, token):
        verification_params = f'?uidb64={uidb64}&token={token}'
        return self.request.build_absolute_uri(reverse_lazy('international_online_offer:signup')) + verification_params

    def get_resend_verification_link(self):
        return self.request.build_absolute_uri(
            reverse_lazy('sso_profile:resend-verification', kwargs={'step': 'resend'})
        )


class IOOLogin(ResendVerificationMixin, TemplateView):
    form_class = forms.LoginForm
    template_name = 'ioo/login.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            data = {
                'password': form.cleaned_data['password'],
                'login': form.cleaned_data['email'],
            }
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
                form.add_error(
                    '__all__',
                    'Email unverified: we have re-sent you an email containing a link to verify your email address',
                )
            elif upstream_response.status_code == 302:
                # 302 from sso indicate successful login
                cookie_jar = sso_helpers.get_cookie_jar(upstream_response)
                response = HttpResponseRedirect(self.success_url)
                sso_helpers.set_cookies_from_cookie_jar(
                    cookie_jar=cookie_jar,
                    response=response,
                    whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
                )
                return response
            elif upstream_response.status_code == 200:
                # 200 from sso indicate the credentials were not correct
                form.add_error('__all__', 'Invalid email / password')

        return render(request, self.template_name, {'form': form})


class IOOSignUp(ResendVerificationMixin, TemplateView):
    template_name = 'ioo/signup-new.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def get(self, request, *args, **kwargs):
        form = forms.SignUpForm
        if self.is_validate_code_flow():
            form = forms.CodeConfirmForm
        return render(request, self.template_name, {'form': form})

    def get_login_url(self):
        return self.request.build_absolute_uri(reverse_lazy('international_online_offer:login'))

    def is_validate_code_flow(self):
        return self.request.GET.get('uidb64') is not None and self.request.GET.get('token') is not None

    def do_validate_code_flow(self, request):
        form = forms.CodeConfirmForm(request.POST)
        if form.is_valid():
            uidb64 = self.request.GET.get('uidb64')
            token = self.request.GET.get('token')
            code_confirm = form.cleaned_data['code_confirm']
            upstream_response = sso_api_client.user.verify_verification_code(
                {'uidb64': uidb64, 'token': token, 'code': code_confirm}
            )
            if upstream_response.status_code in [400, 404]:
                form.add_error('__all__', 'Invalid code')
            elif upstream_response.status_code == 422:
                # Resend verification code if it has expired.
                email = upstream_response.json()['email']
                verification_code = sso_helpers.regenerate_verification_code(email)
                sso_helpers.send_verification_code_email(
                    email=email,
                    verification_code=verification_code,
                    form_url=request.path,
                    verification_link=self.get_verification_link(uidb64, token),
                    resend_verification_link=self.get_resend_verification_link(),
                )
                form.add_error('__all__', 'Code has expired: we have emailed you a new code')
            else:
                email = upstream_response.json()['email']
                helpers.send_welcome_notification(email=email, form_url=self.request.path)
                cookie_jar = sso_helpers.get_cookie_jar(upstream_response)
                response = HttpResponseRedirect(reverse_lazy('international_online_offer:profile'))
                sso_helpers.set_cookies_from_cookie_jar(
                    cookie_jar=cookie_jar,
                    response=response,
                    whitelist=[settings.SSO_SESSION_COOKIE, settings.SSO_DISPLAY_LOGGED_IN_COOKIE],
                )
                return response

        return render(request, self.template_name, {'form': form})

    def do_sign_up_flow(self, request):
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            response = sso_api_client.user.create_user(
                email=form.cleaned_data['email'].lower(), password=form.cleaned_data['password']
            )
            if response.status_code == 400:
                server_errors = response.json()
                for attribute, value in server_errors.items():
                    form.add_error(attribute, value)
            elif response.status_code == 409:
                email = form.cleaned_data['email'].lower()
                verification_code = sso_helpers.regenerate_verification_code(email)
                if verification_code:
                    uidb64 = verification_code.pop('user_uidb64')
                    token = verification_code.pop('verification_token')
                    sso_helpers.send_verification_code_email(
                        email=email,
                        verification_code=verification_code,
                        form_url=self.request.path,
                        verification_link=self.get_verification_link(uidb64, token),
                        resend_verification_link=self.get_resend_verification_link(),
                    )
                    form.add_error('__all__', 'We have sent you an email containing a code to verify your account')
                else:
                    sso_helpers.notify_already_registered(
                        email=email, form_url=self.request.path, login_url=self.get_login_url()
                    )
                    form.add_error('__all__', 'Already registered: we have sent you an email regarding your account')
            elif response.status_code == 201:
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
                return HttpResponseRedirect(
                    reverse_lazy('international_online_offer:signup') + '?uidb64=' + uidb64 + '&token=' + token
                )

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if self.is_validate_code_flow():
            return self.do_validate_code_flow(request)
        else:
            return self.do_sign_up_flow(request)


class IOOEditYourAnswers(TemplateView):
    template_name = 'ioo/edit_your_answers.html'

    def get_context_data(self, **kwargs):
        triage_data = get_triage_data_from_db_or_session(self.request)
        user_data = get_user_data_from_db_or_session(self.request)
        return super().get_context_data(
            **kwargs,
            triage_data=triage_data,
            user_data=user_data,
            back_url='/international/expand-your-business-in-the-uk/guide/',
        )
