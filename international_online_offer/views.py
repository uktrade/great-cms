from directory_forms_api_client import actions
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
from international_online_offer.services import get_bci_data, get_dbt_sectors
from sso import helpers as sso_helpers, mixins as sso_mixins


def calculate_and_store_is_high_value(request):
    dbt_sectors = get_dbt_sectors()
    existing_triage_data = get_triage_data_for_user(request)
    sector = existing_triage_data.sector

    if existing_triage_data.sector_id:
        sector_row = region_sector_helpers.get_sector(existing_triage_data.sector_id, dbt_sectors)
        if sector_row:
            sector = sector_row['full_sector_name']

    is_high_value = scorecard.score_is_high_value(
        sector,
        existing_triage_data.location,
        existing_triage_data.hiring,
        existing_triage_data.spend,
        request.user.hashed_uuid,
    )

    if request.user.is_authenticated:
        TriageData.objects.update_or_create(
            hashed_uuid=request.user.hashed_uuid, defaults={'is_high_value': is_high_value}
        )


class IndexView(GA360Mixin, TemplateView):
    template_name = 'eyb/index.html'

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


class AboutYourBusinessView(GA360Mixin, TemplateView):
    template_name = 'eyb/about_your_business.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='AboutYourBusiness',
            business_unit='ExpandYourBusiness',
            site_section='about-your-business',
        )

    def get_context_data(self, *args, **kwargs):
        # Signup has occured
        UserData.objects.update_or_create(
            hashed_uuid=self.request.user.hashed_uuid,
            defaults={
                'email': self.request.user.email,
                'agree_terms': True,
            },
        )
        return super().get_context_data(*args, **kwargs)


class BusinessDetailsView(GA360Mixin, FormView):
    template_name = 'eyb/triage/business_details.html'
    form_class = forms.BusinessDetailsForm

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='BusinessDetails',
            business_unit='ExpandYourBusiness',
            site_section='business-details',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:about-your-business')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:know-setup-location')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            user_data = get_user_data_for_user(self.request)

            inital_values_object = {
                'company_name': '',
                'sector_sub': '',
                'company_location': '',
                'company_website': '',
            }

            if triage_data:
                if triage_data.sector_id:
                    inital_values_object['sector_sub'] = triage_data.sector_id

            if user_data:
                inital_values_object['company_name'] = user_data.company_name
                inital_values_object['company_location'] = user_data.company_location
                inital_values_object['company_website'] = user_data.company_website

            return inital_values_object

    def form_valid(self, form):
        sectors_json = get_dbt_sectors()
        selected_sector_id = form.cleaned_data['sector_sub']
        parent_sector, sub_sector, sub_sub_sector = region_sector_helpers.get_sectors_by_selected_id(
            sectors_json, selected_sector_id
        )

        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'sector': parent_sector,
                    'sector_sub': sub_sector,
                    'sector_sub_sub': sub_sub_sector,
                    'sector_id': selected_sector_id,
                },
            )

            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'company_name': form.cleaned_data['company_name'],
                    'company_location': form.cleaned_data['company_location'],
                    'company_website': form.cleaned_data['company_website'],
                },
            )
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            autocomplete_sector_data=autocomplete_sector_data,
        )


class ContactDetailsView(GA360Mixin, FormView):
    template_name = 'eyb/triage/contact_details.html'
    form_class = forms.ContactDetailsForm

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='ContactDetails',
            business_unit='ExpandYourBusiness',
            site_section='contact-details',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:spend')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = '/international/expand-your-business-in-the-uk/guide/'
        next_url += '?signup=true' if self.request.GET.signup else ''
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_initial(self):
        if self.request.user.is_authenticated:
            user_data = get_user_data_for_user(self.request)

            inital_values_object = {
                'full_name': '',
                'role': '',
                'telephone_number': '',
                'agree_info_email': False,
            }

            if user_data:
                inital_values_object['full_name'] = user_data.full_name
                inital_values_object['role'] = user_data.role
                inital_values_object['telephone_number'] = user_data.telephone_number
                inital_values_object['agree_info_email'] = user_data.agree_info_email

            return inital_values_object

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            self.request.GET.signup = True
            user_data = UserData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            # Check if this is a first time use / signup to show message on guide page
            if not user_data.full_name and user_data.role and user_data.telephone_number:
                self.request.GET.signup = True
            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'full_name': form.cleaned_data['full_name'],
                    'role': form.cleaned_data['role'],
                    'telephone_number': form.cleaned_data['telephone_number'],
                    'agree_info_email': form.cleaned_data['agree_info_email'],
                },
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        leading_title = 'Provide your details so that we can contact you - we may be able to help.'
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                if triage_data.is_high_value:
                    leading_title = """You may be eligible for one-to-one support for your expansion.
                    Provide your details so that an adviser can contact you to discuss your plans."""

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            leading_title=leading_title,
        )


class KnowSetupLocationView(GA360Mixin, FormView):
    form_class = forms.KnowSetupLocationForm
    template_name = 'eyb/triage/know_your_setup_location.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='DoYouKnowYourSetupLocation',
            business_unit='ExpandYourBusiness',
            site_section='do-you-know-your-setup-location',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:business-details')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:location')
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                if triage_data.location_none:
                    next_url = reverse_lazy('international_online_offer:when-want-setup')

        if self.request.GET.get('next'):
            if not triage_data.location_none:
                next_url += '?next=' + check_url_host_is_safelisted(self.request)
            else:
                next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                know_setup_location = None
                if triage_data.location_none is True:
                    know_setup_location = False
                elif triage_data.location_none is False:
                    know_setup_location = True
                return {'know_setup_location': know_setup_location}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            user_knows_where_they_want_to_setup = True if form.cleaned_data['know_setup_location'] == 'True' else False
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'location_none': not user_knows_where_they_want_to_setup,
                },
            )
            if not user_knows_where_they_want_to_setup:
                TriageData.objects.update_or_create(
                    hashed_uuid=self.request.user.hashed_uuid,
                    defaults={
                        'location': '',
                        'location_city': None,
                    },
                )
        calculate_and_store_is_high_value(self.request)
        return super().form_valid(form)


class WhenDoYouWantToSetupView(GA360Mixin, FormView):
    form_class = forms.WhenDoYouWantToSetupForm
    template_name = 'eyb/triage/when_want_to_setup.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='WhenDoYouWantToSetup',
            business_unit='ExpandYourBusiness',
            site_section='when-do-you-want-to-setup',
        )

    def get_back_url(self):
        back_url = reverse_lazy('international_online_offer:location')
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                if triage_data.location_none:
                    back_url = reverse_lazy('international_online_offer:know-setup-location')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:intent')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            user_data = get_user_data_for_user(self.request)
            if user_data:
                return {'landing_timeframe': user_data.landing_timeframe}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'landing_timeframe': form.cleaned_data['landing_timeframe'],
                },
            )
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
        back_url = reverse_lazy('international_online_offer:when-want-setup')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:hiring')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                return {'intent': triage_data.intent, 'intent_other': triage_data.intent_other}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'intent': form.cleaned_data['intent'],
                    'intent_other': form.cleaned_data['intent_other'],
                },
            )
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
        back_url = reverse_lazy('international_online_offer:know-setup-location')
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        next_url = reverse_lazy('international_online_offer:when-want-setup')
        if self.request.GET.get('next'):
            next_url = check_url_host_is_safelisted(self.request)
        return next_url

    def get_context_data(self, **kwargs):
        region = None
        city = None
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                region = triage_data.get_location_display()
                city = triage_data.get_location_city_display()

        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
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
                    'location_none': False,
                },
            )
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
        back_url = reverse_lazy('international_online_offer:intent')
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
        )

    def get_initial(self):
        if self.request.user.is_authenticated:
            triage_data = get_triage_data_for_user(self.request)
            if triage_data:
                return {'hiring': triage_data.hiring}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'hiring': form.cleaned_data['hiring'],
                },
            )
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
        next_url = reverse_lazy('international_online_offer:contact-details')
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

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'spend': form.cleaned_data['spend'],
                },
            )
        calculate_and_store_is_high_value(self.request)
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
        code_expired_error = {'field': '__all__', 'error_message': 'The security code has expired. New code sent'}
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
            return redirect(reverse_lazy('international_online_offer:about-your-business'))
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
                form.add_error('code_confirm', 'Enter a correct confirmation code')
            elif upstream_response.status_code == 422:
                # Resend verification code if it has expired.
                form.add_error('code_confirm', 'The security code has expired. New code sent')
                self.handle_code_expired(
                    upstream_response, request, form, verification_link=self.get_verification_link(uidb64, token)
                )
            else:
                return self.handle_verification_code_success(
                    upstream_response=upstream_response,
                    redirect_url=reverse_lazy('international_online_offer:about-your-business') + '?signup=true',
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
                    reverse_lazy('international_online_offer:signup')
                    + '?uidb64='
                    + uidb64
                    + '&token='
                    + token
                    + '&email='
                    + user_details['email']
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
        spend_choices = helpers.get_spend_choices_by_currency(self.request.session.get('spend_currency'))

        sub_and_sub_sub_sector = '-'
        spend = '-'
        if triage_data:
            if triage_data.sector_sub:
                sub_and_sub_sub_sector = triage_data.sector_sub
                if triage_data.sector_sub_sub:
                    sub_and_sub_sub_sector = sub_and_sub_sub_sector + ', ' + triage_data.sector_sub_sub

            for spend_choice in spend_choices:
                if spend_choice[0] == triage_data.spend:
                    spend = spend_choice[1]

        return super().get_context_data(
            **kwargs,
            triage_data=triage_data,
            user_data=user_data,
            back_url='/international/expand-your-business-in-the-uk/guide/',
            spend=spend,
            sub_and_sub_sub_sector=sub_and_sub_sub_sector,
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
                Q(sector__icontains=triage_data.sector) | Q(sector__in=trade_association_sectors)
            )

        page = self.request.GET.get('page', 1)
        paginator = Paginator(all_trade_associations, 20)
        all_trade_associations = paginator.page(page)

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#tailored-guide'},
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
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#tailored-guide'},
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
