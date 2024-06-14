from directory_forms_api_client import actions
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from core.helpers import check_url_host_is_safelisted
from directory_sso_api_client import sso_api_client
from international_online_offer import forms
from international_online_offer.core import (
    helpers,
    region_sector_helpers,
    regions,
    scorecard,
)
from international_online_offer.models import (
    CsatFeedback,
    TradeAssociation,
    TriageData,
    UserData,
    get_triage_data_for_user,
    get_user_data_for_user,
)
from international_online_offer.services import get_bci_data
from sso import helpers as sso_helpers, mixins as sso_mixins


def calculate_and_store_is_high_value(request):
    existing_triage_data = get_triage_data_for_user(request)
    dbt_sub_sector_from_sic_sector = region_sector_helpers.get_full_sector_name_from_sic_sector(
        existing_triage_data.sector_sub
    )
    is_high_value = scorecard.score_is_high_value(
        existing_triage_data.sector,
        dbt_sub_sector_from_sic_sector,
        existing_triage_data.location,
        existing_triage_data.hiring,
        existing_triage_data.spend,
    )
    if request.user.is_authenticated:
        TriageData.objects.update_or_create(
            hashed_uuid=request.user.hashed_uuid, defaults={'is_high_value': is_high_value}
        )
    else:
        request.session['is_high_value'] = is_high_value


class IndexView(GA360Mixin, TemplateView):
    template_name = 'eyb/index.html'
    # TODO remove after general election AND sign up to front branch merged
    if settings.FEATURE_PRE_ELECTION and settings.FEATURE_EYB_HOME:
        template_name = 'eyb/index-new.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Index',
            business_unit='ExpandYourBusiness',
            site_section='index',
        )

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]
        return super().get_context_data(
            **kwargs,
            breadcrumbs=breadcrumbs,
        )


class SectorView(GA360Mixin, FormView):
    form_class = forms.SectorForm
    template_name = 'eyb/triage/sector.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Sector',
            business_unit='ExpandYourBusiness',
            site_section='sector',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:index')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:intent')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        sector = self.request.session.get('sector')
        sector_sub = self.request.session.get('sector_sub')
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                sector = triage_data.get_sector_display()
                sector_sub = triage_data.get_sector_sub_display()

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 1 of 5',
            question_text='What does your company make or do?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your sector and products or services.""",
            autocomplete_sector_data=region_sector_helpers.get_sectors_and_sic_sectors_file_as_string(),
            sector_sub=sector_sub,
            sector=sector,
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                return {'sector_sub': triage_data.sector_sub}

        return {'sector_sub': self.request.session.get('sector_sub')}

    def form_valid(self, form):
        sub_sector = form.cleaned_data['sector_sub']
        sector = region_sector_helpers.get_sector_from_sic_sector(sub_sector)
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'sector': sector,
                    'sector_sub': form.cleaned_data['sector_sub'],
                },
            )
        else:
            self.request.session['sector'] = sector
            self.request.session['sector_sub'] = form.cleaned_data['sector_sub']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class IntentView(GA360Mixin, FormView):
    form_class = forms.IntentForm
    template_name = 'eyb/triage/intent.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Intent',
            business_unit='ExpandYourBusiness',
            site_section='intent',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:sector')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:location')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
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
            triage_data = get_triage_data_for_user(self.request)
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


class LocationView(GA360Mixin, FormView):
    form_class = forms.LocationForm
    template_name = 'eyb/triage/location.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Location',
            business_unit='ExpandYourBusiness',
            site_section='location',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:intent')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:hiring')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        region = self.request.session.get('location')
        city = self.request.session.get('location_city')
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                region = triage_data.get_location_display()
                city = triage_data.get_location_city_display()

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 3 of 5',
            question_text='Where in the UK would you like to expand your business?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your city, county or region.""",
            autocomplete_location_data=region_sector_helpers.get_region_and_cities_json_file_as_string(),
            region=region,
            city=city,
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                location = triage_data.location_city if triage_data.location_city else triage_data.location
                return {'location': location, 'location_none': triage_data.location_none}

        location = (
            self.request.session.get('location_city')
            if self.request.session.get('location_city')
            else self.request.session.get('location')
        )
        return {
            'location': location,
            'location_none': self.request.session.get('location_none'),
        }

    def form_valid(self, form):
        region = None
        city = None
        if region_sector_helpers.is_region(form.cleaned_data['location']):
            region = form.cleaned_data['location']
        else:
            region = region_sector_helpers.get_region_from_city(form.cleaned_data['location'])
            city = form.cleaned_data['location']

        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'location': region,
                    'location_city': city,
                    'location_none': form.cleaned_data['location_none'],
                },
            )
        else:
            self.request.session['location'] = region
            self.request.session['location_city'] = city
            self.request.session['location_none'] = form.cleaned_data['location_none']
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class HiringView(GA360Mixin, FormView):
    form_class = forms.HiringForm
    template_name = 'eyb/triage/hiring.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Hiring',
            business_unit='ExpandYourBusiness',
            site_section='hiring',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:location')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:spend')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
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
            triage_data = get_triage_data_for_user(self.request)
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


class SpendView(GA360Mixin, FormView):
    form_class = forms.SpendForm
    template_name = 'eyb/triage/spend.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Spend',
            business_unit='ExpandYourBusiness',
            site_section='spend',
        )

    def get_form_kwargs(self):
        kwargs = super(SpendView, self).get_form_kwargs()
        spend_currency = self.request.session.get('spend_currency')
        kwargs['spend_currency'] = spend_currency
        return kwargs

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:hiring')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)

        return back_url

    def get_success_url(self):
        next_url = '/international/expand-your-business-in-the-uk/guide/'
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        spend_currency_param = self.request.GET.get('spend_currency')
        if spend_currency_param:
            self.request.session['spend_currency'] = spend_currency_param

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            step_text='Step 5 of 5',
            question_text='How much do you want to spend on setting up in the first three years?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your spend.""",
            spend_currency_form=forms.SpendCurrencySelectForm(
                initial={'spend_currency': self.request.session.get('spend_currency')}
            ),
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                return {'spend': triage_data.spend, 'spend_currency': self.request.session.get('spend_currency')}

        return {
            'spend': self.request.session.get('spend'),
            'spend_currency': self.request.session.get('spend_currency'),
        }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'spend': form.cleaned_data['spend'],
                },
            )
        else:
            self.request.session['spend'] = form.cleaned_data['spend']

        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class ProfileView(GA360Mixin, FormView):
    form_class = forms.ProfileForm
    template_name = 'eyb/profile.html'

    def get_success_url(self) -> str:
        if self.request.GET.get('signup'):
            return '/international/expand-your-business-in-the-uk/guide/?signup=true'
        return '/international/expand-your-business-in-the-uk/guide/'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Profile',
            business_unit='ExpandYourBusiness',
            site_section='profile',
        )

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
        user_data = get_user_data_for_user(self.request)
        # if user_data has been provided then the user has setup a profile before
        if user_data:
            title = self.PROFILE_DETAILS_TITLE
            sub_title = self.PROFILE_DETAILS_SUB_TITLE

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
        ]
        return super().get_context_data(
            **kwargs,
            title=title,
            sub_title=sub_title,
            breadcrumbs=breadcrumbs,
        )

    def get_initial(self):
        email = self.request.user.email
        # Setting form data up for first time use (signup)
        init_user_form_data = {
            'company_name': '',
            'company_location': '',
            'full_name': '',
            'role': '',
            'email': email,
            'telephone_number': '',
            'agree_terms': True,
            'agree_info_email': '',
            'landing_timeframe': '',
            'company_website': '',
        }
        user_data = get_user_data_for_user(self.request)
        if user_data:
            # If user_data then we're dealing with an existing user accessing their profile
            init_user_form_data['email'] = user_data.email
            init_user_form_data['company_name'] = user_data.company_name
            init_user_form_data['company_location'] = user_data.company_location
            init_user_form_data['full_name'] = user_data.full_name
            init_user_form_data['role'] = user_data.role
            init_user_form_data['telephone_number'] = user_data.telephone_number
            init_user_form_data['agree_terms'] = user_data.agree_terms
            init_user_form_data['agree_info_email'] = user_data.agree_info_email
            init_user_form_data['landing_timeframe'] = user_data.landing_timeframe
            init_user_form_data['company_website'] = user_data.company_website

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
                'sector_sub',
                'intent',
                'intent_other',
                'location',
                'location_city',
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


class LoginView(GA360Mixin, sso_mixins.SignInMixin, TemplateView):
    form_class = forms.LoginForm
    template_name = 'eyb/login.html'
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


class SignUpView(
    GA360Mixin, sso_mixins.ResendVerificationMixin, sso_mixins.VerifyCodeMixin, sso_mixins.SignUpMixin, TemplateView
):
    template_name = 'eyb/signup.html'
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
        if helpers.is_authenticated(request):
            return redirect(reverse_lazy('international_online_offer:profile') + '?signup=true')
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
                form.add_error('__all__', 'You have entered an invalid code')
            elif upstream_response.status_code == 422:
                # Resend verification code if it has expired.
                self.handle_code_expired(
                    upstream_response, request, form, verification_link=self.get_verification_link(uidb64, token)
                )
            else:
                return self.handle_verification_code_success(
                    upstream_response=upstream_response,
                    redirect_url=reverse_lazy('international_online_offer:profile') + '?signup=true',
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


class EditYourAnswersView(GA360Mixin, TemplateView):
    template_name = 'eyb/edit_your_answers.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='EditYourAnswers',
            business_unit='ExpandYourBusiness',
            site_section='change-your-answers',
        )

    def get_context_data(self, **kwargs):
        triage_data = get_triage_data_for_user(self.request)
        user_data = get_user_data_for_user(self.request)
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
        ]
        return super().get_context_data(
            **kwargs,
            triage_data=triage_data,
            user_data=user_data,
            breadcrumbs=breadcrumbs,
        )


class FeedbackView(GA360Mixin, FormView):
    form_class = forms.FeedbackForm
    template_name = 'eyb/feedback.html'
    subject = 'EYB Feedback form'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Feedback',
            business_unit='ExpandYourBusiness',
            site_section='feedback',
        )

    def get_back_url(self):
        back_url = '/international/expand-your-business-in-the-uk/guide/'
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        success_url = reverse_lazy('international_online_offer:feedback') + '?success=true'
        if self.request.GET.get('next'):
            success_url = success_url + '&next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, back_url=self.get_back_url())

    def submit_feedback(self, form):
        cleaned_data = form.cleaned_data
        if self.request.GET.get('next'):
            cleaned_data['from_url'] = check_url_host_is_safelisted(self.request)

        action = actions.SaveOnlyInDatabaseAction(
            full_name='EYB User',
            subject=self.subject,
            email_address='anonymous-user@expand-your-business.trade.gov.uk',
            form_url=self.request.get_full_path(),
        )

        response = action.save(cleaned_data)
        response.raise_for_status()

    def form_valid(self, form):
        self.submit_feedback(form)
        return super().form_valid(form)


class CsatWidgetView(FormView):
    def post(self, request, *args, **kwargs):
        satisfaction = request.POST.get('satisfaction')
        user_journey = request.POST.get('user_journey')
        url = check_url_host_is_safelisted(request)
        request.session['csat_user_journey'] = user_journey

        if satisfaction:
            csat_feedback = CsatFeedback.objects.create(
                satisfaction_rating=satisfaction, URL=url, user_journey=user_journey
            )
            request.session['csat_complete'] = True
            request.session['csat_id'] = csat_feedback.id

        response = HttpResponseRedirect(reverse_lazy('international_online_offer:csat-feedback') + '?next=' + url)
        return response


class CsatFeedbackView(GA360Mixin, FormView):
    form_class = forms.CsatFeedbackForm
    template_name = 'eyb/csat_feedback.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='CSAT Feedback',
            business_unit='ExpandYourBusiness',
            site_section='csat-feedback',
        )

    def get_initial(self):
        csat_id = self.request.session.get('csat_id')
        if csat_id:
            csat_record = CsatFeedback.objects.get(id=csat_id)
            satisfaction = csat_record.satisfaction_rating
            if satisfaction:
                return {'satisfaction': satisfaction}
        else:
            return {'satisfaction': ''}

    def get_success_url(self):
        success_url = reverse_lazy('international_online_offer:csat-feedback') + '?success=true'
        if self.request.GET.get('next'):
            success_url = success_url + '&next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def form_valid(self, form):
        csat_id = self.request.session.get('csat_id')
        if csat_id:
            CsatFeedback.objects.update_or_create(
                id=csat_id,
                defaults={
                    'experienced_issue': form.cleaned_data['experience'],
                    'other_detail': form.cleaned_data['experience_other'],
                    'likelihood_of_return': form.cleaned_data['likelihood_of_return'],
                    'site_intentions': form.cleaned_data['site_intentions'],
                    'site_intentions_other': form.cleaned_data['site_intentions_other'],
                    'service_improvements_feedback': form.cleaned_data['feedback_text'],
                },
            )
            if self.request.session.get('csat_id'):
                del self.request.session['csat_id']
        else:
            CsatFeedback.objects.create(
                satisfaction_rating=form.cleaned_data['satisfaction'],
                experienced_issue=form.cleaned_data['experience'],
                other_detail=form.cleaned_data['experience_other'],
                likelihood_of_return=form.cleaned_data['likelihood_of_return'],
                site_intentions=form.cleaned_data['site_intentions'],
                service_improvements_feedback=form.cleaned_data['feedback_text'],
                site_intentions_other=form.cleaned_data['site_intentions_other'],
                URL=check_url_host_is_safelisted(self.request),
                user_journey=self.request.session.get('csat_user_journey'),
            )
            if self.request.session.get('csat_user_journey'):
                del self.request.session['csat_user_journey']
        return super().form_valid(form)


class TradeAssociationsView(GA360Mixin, TemplateView):
    template_name = 'eyb/trade_associations.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='TradeAssociations',
            business_unit='ExpandYourBusiness',
            site_section='trade-associations',
        )

    def get_context_data(self, **kwargs):
        triage_data = get_triage_data_for_user(self.request)
        all_trade_associations = []

        if triage_data:
            # Try getting trade associations by exact sector match or in mapped list of sectors
            trade_association_sectors = helpers.get_trade_assoication_sectors_from_sector(triage_data.sector)

            all_trade_associations = TradeAssociation.objects.filter(
                Q(sector__icontains=triage_data.get_sector_display()) | Q(sector__in=trade_association_sectors)
            )

        page = self.request.GET.get('page', 1)
        paginator = Paginator(all_trade_associations, 20)
        all_trade_associations = paginator.page(page)

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
        ]

        return super().get_context_data(
            triage_data=triage_data,
            all_trade_associations=all_trade_associations,
            breadcrumbs=breadcrumbs,
            **kwargs,
        )


class BusinessClusterView(GA360Mixin, TemplateView):
    template_name = 'eyb/bci.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='BCI',
            business_unit='ExpandYourBusiness',
            site_section='business-cluster-information',
        )

    def get(self, *args, **kwargs):
        triage_data = get_triage_data_for_user(self.request)

        # an edge case where a user doesn't have triage data or a sector in which case
        # it isn't possible to display meaningful bci information
        if not triage_data or not triage_data.sector:
            return redirect(reverse_lazy('international_online_offer:sector'))

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
        ]

        geo_area = self.request.GET.get('area', None)

        # We are in a region view, add link back to parent bci page (UK nations)
        if geo_area != regions.GB_GEO_CODE:
            breadcrumbs.append(
                {
                    'name': 'UK market data',
                    'url': '/international/expand-your-business-in-the-uk/business-cluster-information/?area=K03000001',
                }
            )

        triage_data = get_triage_data_for_user(self.request)

        (bci_headline, headline_region, bci_detail, bci_release_year, hyperlinked_geo_codes) = get_bci_data(
            triage_data.sector, geo_area
        )

        # sort alphabetically by geo description
        bci_detail = sorted(bci_detail, key=lambda e: e['geo_description'])

        return super().get_context_data(
            triage_data=triage_data,
            breadcrumbs=breadcrumbs,
            bci_headline=bci_headline,
            bci_detail=bci_detail,
            hyperlinked_geo_codes=hyperlinked_geo_codes,
            bci_release_year=bci_release_year,
            headline_region=headline_region,
            **kwargs,
        )
