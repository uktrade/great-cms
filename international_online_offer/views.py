from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from directory_sso_api_client import sso_api_client
from international_online_offer import forms
from international_online_offer.core import helpers, scorecard
from international_online_offer.models import (
    TriageData,
    UserData,
    get_triage_data,
    get_triage_data_from_db_or_session,
    get_user_data,
    get_user_data_from_db_or_session,
)
from sso import helpers as sso_helpers, mixins as sso_mixins


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


class IOOIndex(GA360Mixin, TemplateView):
    template_name = 'ioo/index.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Index',
            business_unit='ExpandYourBusiness',
            site_section='index',
        )


class IOOSector(GA360Mixin, FormView):
    form_class = forms.SectorForm
    template_name = 'ioo/triage/sector.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Sector',
            business_unit='ExpandYourBusiness',
            site_section='sector',
        )

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


class IOOIntent(GA360Mixin, FormView):
    form_class = forms.IntentForm
    template_name = 'ioo/triage/intent.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Intent',
            business_unit='ExpandYourBusiness',
            site_section='intent',
        )

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


class IOOLocation(GA360Mixin, FormView):
    form_class = forms.LocationForm
    template_name = 'ioo/triage/location.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Location',
            business_unit='ExpandYourBusiness',
            site_section='location',
        )

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


class IOOHiring(GA360Mixin, FormView):
    form_class = forms.HiringForm
    template_name = 'ioo/triage/hiring.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Hiring',
            business_unit='ExpandYourBusiness',
            site_section='hiring',
        )

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


class IOOSpend(GA360Mixin, FormView):
    form_class = forms.SpendForm
    template_name = 'ioo/triage/spend.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Spend',
            business_unit='ExpandYourBusiness',
            site_section='spend',
        )

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


class IOOProfile(GA360Mixin, FormView):
    form_class = forms.ProfileForm
    template_name = 'ioo/profile.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Profile',
            business_unit='ExpandYourBusiness',
            site_section='profile',
        )

    success_url = '/international/expand-your-business-in-the-uk/guide/'
    COMPLETE_SIGN_UP_TITLE = 'Complete sign up'
    COMPLETE_SIGN_UP_LOW_VALUE_SUB_TITLE = 'Complete the sign up form to access your full personalised guide.'
    COMPLETE_SIGN_UP_HIGH_VALUE_SUB_TITLE = (
        'Complete the sign up form to access 1 to 1 support and your full personalised guide.'
    )

    PROFILE_DETAILS_TITLE = 'Profile details'
    PROFILE_DETAILS_SUB_TITLE = 'Update your profile information below.'

    def get_context_data(self, **kwargs):
        title = self.COMPLETE_SIGN_UP_TITLE
        sub_title = self.COMPLETE_SIGN_UP_LOW_VALUE_SUB_TITLE
        user_data = get_user_data_from_db_or_session(self.request)
        triage_data = get_triage_data_from_db_or_session(self.request)
        # if full_name has been provided then the user has setup a profile before
        if user_data.full_name:
            title = self.PROFILE_DETAILS_TITLE
            sub_title = self.PROFILE_DETAILS_SUB_TITLE
        elif triage_data.is_high_value:
            sub_title = self.COMPLETE_SIGN_UP_HIGH_VALUE_SUB_TITLE

        return super().get_context_data(
            **kwargs,
            title=title,
            sub_title=sub_title,
            back_url='/international/expand-your-business-in-the-uk/guide/',
        )

    def get_initial(self):
        email = ''
        if self.request.user.email:
            email = self.request.user.email
        init_user_form_data = {
            'company_name': '',
            'company_location': '',
            'full_name': '',
            'role': '',
            'email': email,
            'telephone_number': '',
            'agree_terms': True,
            'agree_info_email': '',
            'agree_info_telephone': '',
        }
        if self.request.user.is_authenticated:
            user_data = get_user_data(self.request.user.hashed_uuid)
            if user_data:
                init_user_form_data['email'] = user_data.email
                init_user_form_data['company_name'] = user_data.company_name
                init_user_form_data['company_location'] = user_data.company_location
                init_user_form_data['full_name'] = user_data.full_name
                init_user_form_data['role'] = user_data.role
                init_user_form_data['telephone_number'] = user_data.telephone_number
                init_user_form_data['agree_terms'] = user_data.agree_terms
                init_user_form_data['agree_info_email'] = user_data.agree_info_email
                init_user_form_data['agree_info_telephone'] = user_data.agree_info_telephone

        return init_user_form_data

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults=form.cleaned_data,
            )

            session_data_triage_object = {}
            for key in [
                'sector',
                'intent',
                'intent_other',
                'location',
                'location_none',
                'hiring',
                'spend',
                'spend_other',
                'is_high_value',
            ]:
                if self.request.session.get(key):
                    session_data_triage_object[key] = self.request.session.get(key)
                    del self.request.session[key]

            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults=session_data_triage_object,
            )

        return super().form_valid(form)


class IOOLogin(GA360Mixin, sso_mixins.SignInMixin, TemplateView):
    form_class = forms.LoginForm
    template_name = 'ioo/login.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Login',
            business_unit='ExpandYourBusiness',
            site_section='login',
        )

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
            response = self.handle_post_request(
                data,
                form,
                request,
                self.success_url,
            )
            if isinstance(response, HttpResponseRedirect):
                return response
            if response:
                form.add_error('__all__', response)

        return render(request, self.template_name, {'form': form})


class IOOSignUp(
    GA360Mixin, sso_mixins.ResendVerificationMixin, sso_mixins.VerifyCodeMixin, sso_mixins.SignUpMixin, TemplateView
):
    template_name = 'ioo/signup.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def __init__(self):
        code_expired_error = {'field': '__all__', 'error_message': 'Code has expired: we have emailed you a new code'}
        super().__init__(code_expired_error)
        self.set_ga360_payload(
            page_id='Signup',
            business_unit='ExpandYourBusiness',
            site_section='signup',
        )

    def send_welcome_notification(self, email, form_url):
        return helpers.send_welcome_notification(email, form_url)

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
                self.handle_code_expired(
                    upstream_response, request, form, verification_link=self.get_verification_link(uidb64, token)
                )
            else:
                return self.handle_verification_code_success(
                    upstream_response=upstream_response, redirect_url=reverse_lazy('international_online_offer:profile')
                )
        return render(request, self.template_name, {'form': form})

    def do_sign_up_flow(self, request):
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            response = sso_api_client.user.create_user(
                email=form.cleaned_data['email'].lower(), password=form.cleaned_data['password']
            )
            if response.status_code == 400:
                self.handle_400_response(response, form)
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
                redirect_url = (
                    reverse_lazy('international_online_offer:signup') + '?uidb64=' + uidb64 + '&token=' + token
                )
                return self.handle_signup_success(
                    response, form, redirect_url, verification_link=self.get_verification_link(uidb64, token)
                )

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if self.is_validate_code_flow():
            return self.do_validate_code_flow(request)
        else:
            return self.do_sign_up_flow(request)


class IOOEditYourAnswers(GA360Mixin, TemplateView):
    template_name = 'ioo/edit_your_answers.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='EditYourAnswers',
            business_unit='ExpandYourBusiness',
            site_section='edit-your-answers',
        )

    def get_context_data(self, **kwargs):
        triage_data = get_triage_data_from_db_or_session(self.request)
        user_data = get_user_data_from_db_or_session(self.request)
        return super().get_context_data(
            **kwargs,
            triage_data=triage_data,
            user_data=user_data,
            back_url='/international/expand-your-business-in-the-uk/guide/',
        )
