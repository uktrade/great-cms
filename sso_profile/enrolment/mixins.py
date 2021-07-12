import abc
from urllib.parse import unquote

from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from enrolment import constants, helpers
from requests.exceptions import HTTPError

from directory_sso_api_client import sso_api_client


class RestartOnStepSkipped:
    def render(self, *args, **kwargs):
        if self.steps.prev and not self.get_cleaned_data_for_step(self.steps.prev):
            return redirect(reverse('enrolment-business-type'))
        return super().render(*args, **kwargs)


class RemotePasswordValidationError(ValueError):
    def __init__(self, form):
        self.form = form


class RedirectLoggedInMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('about')
        return super().dispatch(request, *args, **kwargs)


class RedirectAlreadyEnrolledMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if helpers.user_has_company(request.user.session_id):
                return redirect('about')
        return super().dispatch(request, *args, **kwargs)


class StepsListMixin(abc.ABC):
    """
    Anonymous users see different steps on the progress indicator. Feature flag
    can also affect the steps shown.

    """

    @property
    @abc.abstractmethod
    def steps_list_labels(self):
        pass  # pragma: no cover

    def should_show_anon_progress_indicator(self):
        if self.request.GET.get('new_enrollment') == 'True':
            return True
        else:
            return self.request.user.is_anonymous

    @property
    def step_labels(self):
        labels = self.steps_list_labels[:]
        if not self.should_show_anon_progress_indicator():
            self.remove_label(labels=labels, label=constants.PROGRESS_STEP_LABEL_USER_ACCOUNT)
            self.remove_label(labels=labels, label=constants.PROGRESS_STEP_LABEL_VERIFICATION)
            if self.request.user.has_user_profile:
                self.remove_label(labels=labels, label=constants.PROGRESS_STEP_LABEL_PERSONAL_INFO)
        return labels

    def remove_label(self, labels, label):
        if label in labels:
            labels.remove(label)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(step_labels=self.step_labels, step_number=1, *args, **kwargs)


class ProgressIndicatorMixin:
    """
    Anonymous users see different numbers next to the steps on the progress
    indicator. Feature flag can also affect this numbering.

    """

    @property
    @abc.abstractmethod
    def progress_conf(self):
        pass  # pragma: no cover

    def get(self, *args, **kwargs):
        if (
            constants.SESSION_KEY_INGRESS_ANON not in self.storage.extra_data
            and self.kwargs['step'] == self.steps.first  # noqa: W503
        ):
            self.storage.extra_data[constants.SESSION_KEY_INGRESS_ANON] = bool(self.request.user.is_anonymous)
        return super().get(*args, **kwargs)

    def should_show_anon_progress_indicator(self):
        if self.storage.extra_data.get(constants.SESSION_KEY_INGRESS_ANON):
            return True
        return self.request.user.is_anonymous

    @property
    def step_counter(self):
        if self.should_show_anon_progress_indicator():
            counter = self.progress_conf.step_counter_anon
        else:
            counter = self.progress_conf.step_counter_user
        return counter

    def get_context_data(self, *args, **kwargs):
        return {**super().get_context_data(*args, **kwargs), 'step_number': self.step_counter[self.steps.current]}


class CreateUserAccountMixin:
    @property
    def verification_link_url(self):
        raise NotImplementedError

    def user_account_condition(self):
        # user has gone straight to verification code entry step, skipping the
        # step where they enter their email. This can happen if:
        # - user submitted the first step then closed the browser and followed
        # the email from another browser session
        # - user submitted the first step then followed the email from another
        # device
        skipped_first_step = (
            self.kwargs['step'] == constants.VERIFICATION
            and constants.USER_ACCOUNT not in self.storage.data['step_data']  # noqa: W503
        )
        if skipped_first_step:
            return False
        return bool(self.request.user.is_anonymous)

    def new_enrollment_condition(self):
        return 'is_new_enrollment' in self.storage.extra_data

    def verification_condition(self):
        return self.request.user.is_anonymous

    def personal_info_condition(self):
        if self.request.user.is_anonymous:
            return True
        return not self.request.user.has_user_profile

    condition_dict = {
        constants.USER_ACCOUNT: user_account_condition,
        constants.VERIFICATION: verification_condition,
        constants.PERSONAL_INFO: personal_info_condition,
    }

    def dispatch(self, *args, **kwargs):
        try:
            return super().dispatch(*args, **kwargs)
        except RemotePasswordValidationError as error:
            return self.render_revalidation_failure(failed_step=constants.USER_ACCOUNT, form=error.form)

    def get_form_initial(self, step):
        form_initial = super().get_form_initial(step)
        if step == constants.VERIFICATION:
            data = self.get_cleaned_data_for_step(constants.USER_ACCOUNT)
            if data:
                form_initial['email'] = data['email']
        return form_initial

    def process_step(self, form):
        if form.prefix == constants.USER_ACCOUNT:
            response = sso_api_client.user.create_user(
                email=form.cleaned_data['email'], password=form.cleaned_data['password']
            )
            if response.status_code == 400:
                errors = response.json()
                if 'password' in errors:
                    self.storage.set_step_data(
                        constants.USER_ACCOUNT, {form.add_prefix('remote_password_error'): errors['password']}
                    )
                    raise RemotePasswordValidationError(form)
                elif 'email' in errors:
                    helpers.notify_already_registered(email=form.cleaned_data['email'], form_url=self.request.path)
            else:
                response.raise_for_status()
                user_details = response.json()
                helpers.send_verification_code_email(
                    email=user_details['email'],
                    verification_code=user_details['verification_code'],
                    form_url=self.request.path,
                    verification_link=self.verification_link_url,
                )
        return super().process_step(form)

    def render_next_step(self, form, **kwargs):
        response = super().render_next_step(form=form, **kwargs)
        if form.prefix == constants.VERIFICATION:
            response = self.validate_code(form=form, response=response)
        return response

    def get_context_data(self, **kwargs):
        return super().get_context_data(new_enrollment_condition=self.new_enrollment_condition(), **kwargs)

    def validate_code(self, form, response):
        try:
            upstream_response = helpers.confirm_verification_code(
                email=form.cleaned_data['email'], verification_code=form.cleaned_data['code']
            )
        except HTTPError as error:
            if error.response.status_code in [400, 404]:
                self.storage.set_step_data(
                    constants.VERIFICATION,
                    {
                        form.add_prefix('email'): [form.cleaned_data['email']],
                        form.add_prefix('code'): [None],
                        form.add_prefix('remote_code_error'): error.response.json()['code'],
                    },
                )
                return self.render_revalidation_failure(failed_step=constants.VERIFICATION, form=form)
            else:
                raise
        else:
            cookies = helpers.parse_set_cookie_header(upstream_response.headers['set-cookie'])
            response.cookies.update(cookies)
            self.storage.extra_data['is_new_enrollment'] = True
            return response


class CreateBusinessProfileMixin:
    def __new__(cls, *args, **kwargs):
        assert constants.FINISHED in cls.templates
        return super().__new__(cls)

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        whitelist = [
            'address_line_1',
            'address_line_2',
            'company_name',
            'company_number',
            'company_type',
            'date_of_creation',
            'sectors',
            'job_title',
            'phone_number',
            'postal_code',
            'sic',
            'website',
        ]
        return {key: value for key, value in data.items() if value and key in whitelist}

    def create_company_profile(self, data):
        user = self.request.user
        helpers.create_company_profile(
            {
                'sso_id': user.id,
                'company_email': user.email,
                'contact_email_address': user.email,
                'name': user.full_name,
                **data,
            }
        )

    # For user that started their journey from sso-profile, take them directly
    # to their business profile, otherwise show them the success page.
    # The motivation is users that started from sso-profle created the business
    # profile as their end goal. Those that started elsewhere created a
    # business profile as a mean to some other end - so show them a success
    # page with a list of places they can go next.

    def done(self, form_list, *args, **kwargs):
        data = self.serialize_form_list(form_list)
        self.create_company_profile(data)
        if self.request.session.get(constants.SESSION_KEY_BUSINESS_PROFILE_INTENT):
            messages.success(self.request, 'Account created')
            del self.request.session[constants.SESSION_KEY_BUSINESS_PROFILE_INTENT]
            return redirect('business-profile')
        elif self.request.session.get(constants.SESSION_KEY_EXPORT_OPPORTUNITY_INTENT):
            del self.request.session[constants.SESSION_KEY_EXPORT_OPPORTUNITY_INTENT]
            return redirect(self.form_session.ingress_url)
        else:
            return TemplateResponse(self.request, self.templates[constants.FINISHED], self.get_finished_context_data())


class ReadUserIntentMixin:
    """Expose whether the user's intent is to create a business profile"""

    LABEL_BUSINESS = 'create a business profile'
    LABEL_ACCOUNT = 'create an account'
    LABEL_BACKFILL_DETAILS = 'update your details'

    def has_business_profile_intent_in_session(self):
        return self.request.session.get(constants.SESSION_KEY_BUSINESS_PROFILE_INTENT)

    def has_backfill_details_intent_in_session(self):
        return self.request.session.get(constants.SESSION_KEY_BACKFILL_DETAILS_INTENT)

    def get_user_journey_verb(self):
        if self.has_backfill_details_intent_in_session():
            return self.LABEL_BACKFILL_DETAILS
        if self.has_business_profile_intent_in_session() or self.request.user.is_authenticated:
            return self.LABEL_BUSINESS
        return self.LABEL_ACCOUNT

    def get_context_data(self, **kwargs):
        return super().get_context_data(user_journey_verb=self.get_user_journey_verb(), **kwargs)


class WriteUserIntentMixin:
    """Save weather the user's has an intent i.e create a business profile"""

    def has_intent_in_querystring(self, intent_name):
        params = self.request.GET
        # catch the case where anonymous user clicked "start now" from FAB
        # landing page then were sent to SSO login and then clicked "sign up"
        # resulting in 'business-profile-intent' in the `next` param
        if params.get('next'):
            try:
                url, querystring, *rest = unquote(params['next']).split('?')
            except ValueError:
                # querystring may be malformed
                pass
            else:
                params = QueryDict(querystring)
        return params.get(intent_name)

    def dispatch(self, *args, **kwargs):
        if self.has_intent_in_querystring('backfill-details-intent'):
            # user was prompted to backfill their company or business
            # details after logging in
            self.request.session[constants.SESSION_KEY_BACKFILL_DETAILS_INTENT] = True
        elif self.has_intent_in_querystring('business-profile-intent') or 'invite_key' in self.request.GET:
            # user has clicked a button to specifically create a business
            # profile. They are signing up because their end goal is to have
            # a business profile. The counter to this scenario is the user
            # started their journey from outside of sso-profile and their
            # intent is to gain access use other services, and creating a
            # business profile is a step towards that goal. The business
            # profile is a means to and end, not the desired end.
            self.request.session[constants.SESSION_KEY_BUSINESS_PROFILE_INTENT] = True
        elif self.has_intent_in_querystring('export-opportunity-intent'):
            # user has clicked a button to apply for export opportunity
            # after they have create an account they will be directed back
            self.request.session[constants.SESSION_KEY_EXPORT_OPPORTUNITY_INTENT] = True
        return super().dispatch(*args, **kwargs)
