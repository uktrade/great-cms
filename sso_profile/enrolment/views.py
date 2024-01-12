from urllib.parse import urlparse

from directory_forms_api_client.helpers import FormSessionMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

import sso_profile.common.forms
import sso_profile.common.mixins
from core.helpers import CompanyParser
from directory_constants import urls, user_roles
from sso import helpers as sso_helpers
from sso_profile.common.helpers import get_company_admins
from sso_profile.enrolment import constants, forms, helpers, mixins

URL_NON_COMPANIES_HOUSE_ENROLMENT = reverse_lazy(
    'sso_profile:enrolment-sole-trader',
    kwargs={
        'step': constants.USER_ACCOUNT,
    },
)
URL_COMPANIES_HOUSE_ENROLMENT = reverse_lazy(
    'sso_profile:enrolment-companies-house',
    kwargs={
        'step': constants.USER_ACCOUNT,
    },
)
URL_INDIVIDUAL_ENROLMENT = reverse_lazy(
    'sso_profile:enrolment-individual',
    kwargs={'step': constants.USER_ACCOUNT},
)
URL_OVERSEAS_BUSINESS_ENROLMENT = reverse_lazy(
    'sso_profile:enrolment-overseas-business',
)


class EnrolmentStartView(
    mixins.RedirectAlreadyEnrolledMixin,
    FormSessionMixin,
    mixins.StepsListMixin,
    mixins.WriteUserIntentMixin,
    mixins.ReadUserIntentMixin,
    TemplateView,
):
    google_analytics_page_id = 'EnrolmentStartPage'
    template_name = 'enrolment/start.html'
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
        constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_BUSINESS_DETAILS,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if helpers.user_has_company(request.user.session_id):
                return redirect('sso_profile:business-profile')
        return super().dispatch(request, *args, **kwargs)


class BusinessTypeRoutingView(
    mixins.RedirectAlreadyEnrolledMixin,
    mixins.StepsListMixin,
    mixins.WriteUserIntentMixin,
    mixins.ReadUserIntentMixin,
    FormView,
):
    google_analytics_page_id = 'EnrolmentBusinessTypeChooser'
    form_class = forms.BusinessType
    template_name = 'enrolment/business-type.html'
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
        constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_BUSINESS_DETAILS,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    def form_valid(self, form):
        choice = form.cleaned_data['choice']
        if choice == constants.COMPANIES_HOUSE_COMPANY:
            url = URL_COMPANIES_HOUSE_ENROLMENT
        elif choice == constants.NON_COMPANIES_HOUSE_COMPANY:
            url = URL_NON_COMPANIES_HOUSE_ENROLMENT
        elif choice == constants.NOT_COMPANY:
            if self.has_business_profile_intent_in_session():
                url = reverse('sso_profile:enrolment-individual-interstitial')
            else:
                url = URL_INDIVIDUAL_ENROLMENT
        elif choice == constants.OVERSEAS_COMPANY:
            url = URL_OVERSEAS_BUSINESS_ENROLMENT
        else:
            raise NotImplementedError()
        self.request.session[constants.SESSION_KEY_COMPANY_CHOICE] = choice
        return redirect(url)


class BaseEnrolmentWizardView(
    mixins.RedirectAlreadyEnrolledMixin,
    FormSessionMixin,
    mixins.RestartOnStepSkipped,
    sso_profile.common.mixins.PreventCaptchaRevalidationMixin,
    sso_profile.common.mixins.CreateUpdateUserProfileMixin,
    mixins.ProgressIndicatorMixin,
    mixins.StepsListMixin,
    mixins.ReadUserIntentMixin,
    mixins.CreateUserAccountMixin,
    NamedUrlSessionWizardView,
):
    def dispatch(self, request, *args, **kwargs):
        is_authentication_required = self.kwargs['step'] not in [constants.USER_ACCOUNT, constants.VERIFICATION]
        if is_authentication_required and request.user.is_anonymous:
            return redirect(reverse('sso_profile:enrolment-start'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        contact_us_url = urls.domestic.CONTACT_US / 'domestic'
        if self.steps.current == constants.COMPANY_SEARCH:
            context['contact_us_url'] = contact_us_url
        elif self.steps.current == constants.BUSINESS_INFO:
            previous_data = self.get_cleaned_data_for_step(constants.COMPANY_SEARCH)
            if previous_data:
                context['is_enrolled'] = helpers.get_is_enrolled(previous_data['company_number'])
                context['contact_us_url'] = contact_us_url
        elif self.steps.current == constants.PERSONAL_INFO:
            context['company'] = self.get_cleaned_data_for_step(constants.BUSINESS_INFO)
        elif self.steps.current == constants.VERIFICATION:
            url = urls.domestic.CONTACT_US / 'triage/great-account/verification-missing/'
            context['verification_missing_url'] = url
        return context

    def get_finished_context_data(self):
        context = {}
        parsed_url = urlparse(self.form_session.ingress_url)
        if parsed_url.netloc == self.request.get_host():
            context['ingress_url'] = self.form_session.ingress_url
        return context

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def process_step(self, form):
        if form.prefix == constants.PERSONAL_INFO:
            self.create_update_user_profile(form)
        return super().process_step(form)

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step=step)
        if step == constants.PERSONAL_INFO:
            # only show if not creating user account. create user account step also shows terms agreed
            form_kwargs['ask_terms_agreed'] = not bool(self.get_cleaned_data_for_step(constants.VERIFICATION))
        return form_kwargs


class CompaniesHouseEnrolmentView(mixins.CreateBusinessProfileMixin, BaseEnrolmentWizardView):
    google_analytics_page_id = 'CompaniesHouseEnrolment'
    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_user={
            constants.COMPANY_SEARCH: 2,
            constants.ADDRESS_SEARCH: 2,
            constants.BUSINESS_INFO: 2,
            constants.PERSONAL_INFO: 3,
        },
        step_counter_anon={
            constants.USER_ACCOUNT: 2,
            constants.VERIFICATION: 3,
            constants.COMPANY_SEARCH: 4,
            constants.ADDRESS_SEARCH: 4,
            constants.BUSINESS_INFO: 4,
            constants.PERSONAL_INFO: 5,
        },
    )
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
        constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_BUSINESS_DETAILS,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    form_list = (
        (constants.USER_ACCOUNT, forms.UserAccount),
        (constants.VERIFICATION, forms.UserAccountVerification),
        (constants.COMPANY_SEARCH, forms.CompaniesHouseCompanySearch),
        (constants.ADDRESS_SEARCH, forms.CompaniesHouseAddressSearch),
        (constants.BUSINESS_INFO, forms.CompaniesHouseBusinessDetails),
        (constants.PERSONAL_INFO, sso_profile.common.forms.PersonalDetails),
    )

    templates = {
        constants.USER_ACCOUNT: 'enrolment/user-account.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.COMPANY_SEARCH: 'enrolment/companies-house-company-search.html',
        constants.ADDRESS_SEARCH: 'enrolment/address-search.html',
        constants.BUSINESS_INFO: 'enrolment/companies-house-business-details.html',
        constants.PERSONAL_INFO: 'enrolment/companies-house-personal-details.html',
        constants.FINISHED: 'enrolment/companies-house-success.html',
    }

    @property
    def verification_link_url(self):
        url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.VERIFICATION})
        return self.request.build_absolute_uri(url)

    def address_search_condition(self):
        company = self.get_cleaned_data_for_step(constants.COMPANY_SEARCH)
        if not company:
            return True
        return helpers.is_companies_house_details_incomplete(company['company_number'])

    condition_dict = {
        constants.ADDRESS_SEARCH: address_search_condition,
        **mixins.CreateUserAccountMixin.condition_dict,
    }

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step=step)
        if step == constants.BUSINESS_INFO:
            previous_data = self.get_cleaned_data_for_step(constants.COMPANY_SEARCH)
            if previous_data:
                form_kwargs['is_enrolled'] = helpers.get_is_enrolled(previous_data['company_number'])
        return form_kwargs

    def get_form_initial(self, step):
        form_initial = super().get_form_initial(step)
        if step == constants.ADDRESS_SEARCH:
            company = self.get_cleaned_data_for_step(constants.COMPANY_SEARCH) or {}
            form_initial['company_name'] = company.get('company_name')
        elif step == constants.BUSINESS_INFO:
            company_search_step_data = self.get_cleaned_data_for_step(constants.COMPANY_SEARCH)
            company_data = helpers.get_companies_house_profile(company_search_step_data['company_number'])
            company = CompanyParser(company_data)
            form_initial['company_name'] = company.name
            form_initial['company_number'] = company.number
            form_initial['sic'] = company.nature_of_business
            form_initial['date_of_creation'] = company.date_of_creation
            if self.address_search_condition():
                address_step_data = self.get_cleaned_data_for_step(constants.ADDRESS_SEARCH) or {}
                form_initial['address'] = address_step_data.get('address')
                form_initial['postal_code'] = address_step_data.get('postal_code')
            else:
                form_initial['address'] = company.address
                form_initial['postal_code'] = company.postcode
        return form_initial

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.steps.current == constants.ADDRESS_SEARCH:
            context['is_in_companies_house'] = True
        return context

    def serialize_form_list(self, form_list):
        return {**super().serialize_form_list(form_list), 'company_type': 'COMPANIES_HOUSE'}

    def done(self, form_list, form_dict, **kwargs):
        data = self.serialize_form_list(form_list)

        if helpers.get_is_enrolled(data['company_number']):
            helpers.create_company_member(
                sso_session_id=self.request.user.session_id,
                data={
                    'company': data['company_number'],
                    'sso_id': self.request.user.id,
                    'company_email': self.request.user.email,
                    'name': self.request.user.full_name,
                    'mobile_number': data.get('phone_number', ''),
                },
            )
            admins = get_company_admins(self.request.user.session_id)
            helpers.notify_company_admins_member_joined(
                admins=admins,
                data={
                    'company_name': data['company_name'],
                    'name': self.request.user.full_name,
                    'email': self.request.user.email,
                    'profile_remove_member_url': self.request.build_absolute_uri(
                        reverse('sso_profile:business-profile-admin-tools')
                    ),
                    'report_abuse_url': urls.domestic.FEEDBACK,
                },
                form_url=self.request.path,
            )
            if self.request.user.role == user_roles.MEMBER:
                messages.add_message(self.request, messages.SUCCESS, 'You are now linked to the profile.')
            return redirect(reverse('sso_profile:business-profile') + '?member_user_linked=true')
        else:
            return super().done(form_list, form_dict=form_dict, **kwargs)


class NonCompaniesHouseEnrolmentView(mixins.CreateBusinessProfileMixin, BaseEnrolmentWizardView):
    google_analytics_page_id = 'NonCompaniesHouseEnrolment'
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
        constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_BUSINESS_DETAILS,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_user={constants.ADDRESS_SEARCH: 2, constants.PERSONAL_INFO: 3},
        step_counter_anon={
            constants.USER_ACCOUNT: 2,
            constants.VERIFICATION: 3,
            constants.ADDRESS_SEARCH: 4,
            constants.PERSONAL_INFO: 5,
        },
    )

    form_list = (
        (constants.USER_ACCOUNT, forms.UserAccount),
        (constants.VERIFICATION, forms.UserAccountVerification),
        (constants.ADDRESS_SEARCH, forms.NonCompaniesHouseSearch),
        (constants.PERSONAL_INFO, sso_profile.common.forms.PersonalDetails),
    )

    templates = {
        constants.USER_ACCOUNT: 'enrolment/user-account.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.ADDRESS_SEARCH: 'enrolment/address-search.html',
        constants.PERSONAL_INFO: 'enrolment/non-companies-house-personal-details.html',
        constants.FINISHED: 'enrolment/non-companies-house-success.html',
    }

    @property
    def verification_link_url(self):
        url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.VERIFICATION})
        return self.request.build_absolute_uri(url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.steps.current == constants.PERSONAL_INFO:
            context['company'] = self.get_cleaned_data_for_step(constants.ADDRESS_SEARCH)
        return context


class IndividualUserEnrolmentInterstitialView(mixins.ReadUserIntentMixin, TemplateView):
    google_analytics_page_id = 'IndividualEnrolmentInterstitial'
    template_name = 'enrolment/individual-interstitial.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.has_business_profile_intent_in_session():
            url = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.PERSONAL_INFO})
            return redirect(url)
        return super().dispatch(request, *args, **kwargs)


class IndividualUserEnrolmentView(BaseEnrolmentWizardView):
    google_analytics_page_id = 'IndividualEnrolment'
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
        constants.PROGRESS_STEP_LABEL_INDIVIDUAL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_user={constants.PERSONAL_INFO: 3},
        step_counter_anon={constants.USER_ACCOUNT: 2, constants.VERIFICATION: 3, constants.PERSONAL_INFO: 4},
    )

    form_list = (
        (constants.USER_ACCOUNT, forms.UserAccount),
        (constants.VERIFICATION, forms.UserAccountVerification),
        (constants.PERSONAL_INFO, forms.IndividualPersonalDetails),
    )

    templates = {
        constants.USER_ACCOUNT: 'enrolment/individual-user-account.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.PERSONAL_INFO: 'enrolment/individual-personal-details.html',
        constants.FINISHED: 'enrolment/individual-success.html',
    }

    def get(self, *args, **kwargs):
        # at this point all the steps will be hidden as the user is logged
        # in and has a user profile, so the normal `get` method fails with
        # IndexError, meaning `done` will not be hit. Working around this:
        if self.kwargs['step'] == constants.FINISHED:
            return self.done()
        return super().get(*args, **kwargs)

    @property
    def verification_link_url(self):
        url = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.VERIFICATION})
        return self.request.build_absolute_uri(url)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def done(self, *args, **kwargs):
        return TemplateResponse(self.request, self.templates[constants.FINISHED], self.get_finished_context_data())


class CollaboratorEnrolmentView(BaseEnrolmentWizardView):
    google_analytics_page_id = 'CollaboratorEnrolment'
    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_INDIVIDUAL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_user={constants.PERSONAL_INFO: 2},
        step_counter_anon={constants.USER_ACCOUNT: 1, constants.VERIFICATION: 2, constants.PERSONAL_INFO: 3},
    )

    form_list = (
        (constants.USER_ACCOUNT, forms.UserAccountCollaboration),
        (constants.VERIFICATION, forms.UserAccountVerification),
        (constants.PERSONAL_INFO, forms.IndividualPersonalDetails),
    )

    templates = {
        constants.USER_ACCOUNT: 'enrolment/individual-user-account.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.PERSONAL_INFO: 'enrolment/collaborator-personal-details.html',
        constants.FINISHED: 'enrolment/individual-success.html',
        constants.INVITE_EXPIRED: 'enrolment/individual-collaborator-invite-expired.html',
    }

    @property
    def verification_link_url(self):
        url = reverse('sso_profile:enrolment-collaboration', kwargs={'step': constants.VERIFICATION})
        return self.request.build_absolute_uri(url)

    def get(self, *args, **kwargs):
        if 'invite_key' in self.request.GET:
            self.request.session[constants.SESSION_KEY_INVITE_KEY] = self.request.GET['invite_key']
            if not self.collaborator_invition:
                contact_url = urls.domestic.CONTACT_US / 'domestic/enquiries/'
                context = {
                    'contact_url': contact_url,
                    'description': (
                        'This invitation has expired, please contact your business profile administrator to request a '
                        f'new invitation or <a href="{contact_url}"">contact us.</a>'
                    ),
                }
                return TemplateResponse(
                    request=self.request, template=self.templates[constants.INVITE_EXPIRED], context=context
                )
        # at this point all the steps will be hidden as the user is logged
        # in and has a user profile, so the normal `get` method fails with
        # IndexError, meaning `done` will not be hit. Working around this:
        if self.steps.count == 0:
            return self.render_done(form=None, step=constants.FINISHED)
        return super().get(*args, **kwargs)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def create_company_profile(self):
        helpers.collaborator_invite_accept(
            sso_session_id=self.request.user.session_id,
            invite_key=self.request.session[constants.SESSION_KEY_INVITE_KEY],
        )

    @cached_property
    def collaborator_invition(self):
        return helpers.collaborator_invite_retrieve(self.request.session[constants.SESSION_KEY_INVITE_KEY])

    def get_context_data(self, **kwargs):
        return super().get_context_data(collaborator_invition=self.collaborator_invition, **kwargs)

    def get_form_initial(self, step):
        form_initial = super().get_form_initial(step)
        if step == constants.USER_ACCOUNT:
            form_initial['email'] = self.collaborator_invition['collaborator_email']
        return form_initial

    def done(self, *args, **kwargs):
        self.create_company_profile()
        messages.success(self.request, 'Account created')
        return redirect('sso_profile:business-profile')


class PreVerifiedEnrolmentView(BaseEnrolmentWizardView):
    google_analytics_page_id = 'PreVerifiedEnrolment'

    # Needed by CreateUserAccountMixin, not applicable here
    verification_link_url = ''

    steps_list_labels = [
        constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
        constants.PROGRESS_STEP_LABEL_VERIFICATION,
        constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
    ]

    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_user={constants.PERSONAL_INFO: 1},
        step_counter_anon={constants.USER_ACCOUNT: 1, constants.VERIFICATION: 2, constants.PERSONAL_INFO: 3},
    )

    form_list = (
        (constants.USER_ACCOUNT, forms.UserAccount),
        (constants.VERIFICATION, forms.UserAccountVerification),
        (constants.PERSONAL_INFO, sso_profile.common.forms.PersonalDetails),
    )

    templates = {
        constants.USER_ACCOUNT: 'enrolment/user-account.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.PERSONAL_INFO: 'enrolment/preverified-personal-details.html',
    }

    def get(self, *args, **kwargs):
        key = self.request.GET.get('key')
        if key:
            data = helpers.retrieve_preverified_company(key)
            if data:
                self.storage.extra_data[constants.SESSION_KEY_COMPANY_DATA] = data
                self.storage.extra_data[constants.SESSION_KEY_ENROL_KEY] = key
                self.request.session.save()
            else:
                return redirect(reverse('sso_profile:enrolment-start'))
        # at this point all the steps will be hidden as the user is logged
        # in and has a user profile, so the normal `get` method fails with
        # IndexError, meaning `done` will not be hit. Working around this:
        if self.steps.count == 0 or self.kwargs['step'] == constants.FINISHED:
            return self.done()
        if self.steps.current == constants.PERSONAL_INFO:
            if not self.storage.extra_data.get(constants.SESSION_KEY_COMPANY_DATA):
                return redirect(reverse('sso_profile:enrolment-start'))
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.steps.current == constants.PERSONAL_INFO:
            context['company'] = self.storage.extra_data[constants.SESSION_KEY_COMPANY_DATA]
        return context

    def claim_company(self, data):
        helpers.claim_company(
            enrolment_key=self.storage.extra_data[constants.SESSION_KEY_ENROL_KEY],
            personal_name=f'{data["given_name"]} {data["family_name"]}',
            sso_session_id=self.request.user.session_id,
        )

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        return data

    def done(self, *args, **kwargs):
        self.claim_company({'given_name': self.request.user.first_name, 'family_name': self.request.user.last_name})
        messages.success(self.request, 'Business profile created')
        return redirect('sso_profile:business-profile')


class ResendVerificationCodeView(
    mixins.RedirectLoggedInMixin,
    mixins.RestartOnStepSkipped,
    mixins.ProgressIndicatorMixin,
    mixins.StepsListMixin,
    mixins.CreateUserAccountMixin,
    NamedUrlSessionWizardView,
):
    google_analytics_page_id = 'ResendVerificationCode'
    form_list = (
        (constants.RESEND_VERIFICATION, forms.ResendVerificationCode),
        (constants.VERIFICATION, forms.UserAccountVerification),
    )

    templates = {
        constants.RESEND_VERIFICATION: 'enrolment/user-account-resend-verification.html',
        constants.VERIFICATION: 'enrolment/user-account-verification.html',
        constants.FINISHED: 'enrolment/start.html',
    }

    progress_conf = helpers.ProgressIndicatorConf(
        step_counter_anon={constants.RESEND_VERIFICATION: 1, constants.VERIFICATION: 2},
        # logged in users should not get here
        step_counter_user={},
    )
    steps_list_labels = [constants.PROGRESS_STEP_LABEL_RESEND_VERIFICATION, constants.PROGRESS_STEP_LABEL_VERIFICATION]

    @property
    def verification_link_url(self):
        url = reverse('sso_profile:resend-verification', kwargs={'step': constants.VERIFICATION})
        return self.request.build_absolute_uri(url)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def render_done(self, form, **kwargs):
        choice = self.request.session.get(constants.SESSION_KEY_COMPANY_CHOICE)
        if choice == constants.COMPANIES_HOUSE_COMPANY:
            url = URL_COMPANIES_HOUSE_ENROLMENT
        elif choice == constants.NON_COMPANIES_HOUSE_COMPANY:
            url = URL_NON_COMPANIES_HOUSE_ENROLMENT
        elif choice == constants.NOT_COMPANY:
            url = URL_INDIVIDUAL_ENROLMENT
        else:
            url = reverse('sso_profile:enrolment-business-type')
        response = self.validate_code(form=form, response=redirect(url))
        return response

    def process_step(self, form):
        if form.prefix == constants.RESEND_VERIFICATION:
            email = form.cleaned_data['email']
            verification_code = helpers.regenerate_verification_code(email)
            if verification_code:
                sso_helpers.send_verification_code_email(
                    email=email,
                    verification_code=verification_code,
                    form_url=self.request.path,
                    verification_link=self.verification_link_url,
                    resend_verification_link=self.resend_verification_link_url,
                )
        return super().process_step(form)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            verification_missing_url=urls.domestic.CONTACT_US / 'triage/great-account/verification-missing/',
            contact_url=urls.domestic.CONTACT_US / 'domestic/',
            *args,
            **kwargs,
        )

    def get_form_initial(self, step):
        form_initial = super().get_form_initial(step)
        if step == constants.VERIFICATION:
            data = self.get_cleaned_data_for_step(constants.RESEND_VERIFICATION)
            if data:
                form_initial['email'] = data['email']
        return form_initial


class EnrolmentOverseasBusinessView(mixins.ReadUserIntentMixin, TemplateView):
    google_analytics_page_id = 'OverseasBusinessEnrolment'
    template_name = 'enrolment/overseas-business.html'
