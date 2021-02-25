from profile.business_profile import forms, helpers

import sentry_sdk
from directory_api_client.client import api_client
from directory_constants import urls, user_roles
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import DefaultStorage
from django.shortcuts import Http404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import FormView
from formtools.wizard.views import NamedUrlSessionWizardView
from requests.exceptions import HTTPError, RequestException

import core.forms
import core.mixins

BASIC = 'details'
MEDIA = 'images'


class DisconnectFromCompanyMixin:
    form_class = forms.NoOperationForm
    success_message = 'Business profile removed from account.'
    success_url = reverse_lazy('business-profile')

    def form_valid(self, form):
        try:
            helpers.disconnect_from_company(self.request.user.session_id)
        except HTTPError as error:
            if error.response.status_code == 400:
                form.add_error(field=None, error=error.response.json())
                return self.form_invalid(form)
            else:
                raise
        return super().form_valid(form)


class MemberSendAdminRequestMixin:
    form_class = forms.MemberCollaborationRequestForm
    success_url = reverse_lazy('business-profile')

    def form_valid(self, form):
        try:
            if form.cleaned_data['action'] == form.SEND_REQUEST:
                helpers.collaboration_request_create(sso_session_id=self.request.user.session_id, role=user_roles.ADMIN)
            elif form.cleaned_data['action'] == form.SEND_REMINDER:
                helpers.notify_company_admins_collaboration_request_reminder(
                    sso_session_id=self.request.user.session_id,
                    email_data={
                        'company_name': self.request.user.company.data['name'],
                        'name': self.request.user.full_name,
                        'email': self.request.user.email,
                        'login_url': self.request.build_absolute_uri(reverse('business-profile-admin-tools')),
                    },
                    form_url=self.request.path,
                )
        except HTTPError as error:
            if error.response.status_code == 400:
                form.add_error(field=None, error=error.response.json())
                return self.form_invalid(form)
            else:
                raise
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        if cleaned_data['action'] == self.form_class.SEND_REMINDER:
            success_message = 'Your request to the administrator has been sent.'
        elif cleaned_data['action'] == self.form_class.SEND_REQUEST:
            success_message = 'Your request to join has been sent.'
        else:
            raise NotImplementedError
        return success_message


class BusinessProfileView(MemberSendAdminRequestMixin, SuccessMessageMixin, FormView):
    template_name_fab_user = 'business_profile/profile.html'
    template_name_not_fab_user = 'business_profile/is-not-business-profile-user.html'
    template_business_profile_member = 'business_profile/business-profile-member.html'

    def get_template_names(self, *args, **kwargs):
        if self.request.user.company:
            if self.request.user.role == user_roles.MEMBER:
                template_name = self.template_business_profile_member
            else:
                template_name = self.template_name_fab_user
        else:
            template_name = self.template_name_not_fab_user
        return [template_name]

    def get_company(self):
        if self.request.user.is_authenticated and self.request.user.company:
            return self.request.user.company.serialize_for_template()

    def get_business_profile_url(self):
        company = self.get_company()
        if company and company['number']:
            return urls.international.TRADE_FAS / 'suppliers' / company['number'] / company['slug']

    def get_context_data(self, **kwargs):
        company = self.get_company()
        context = super().get_context_data(fab_tab_classes='active', company=company, **kwargs)
        if self.request.user.role == user_roles.MEMBER:
            context.update(
                {
                    'contact_us_url': urls.domestic.CONTACT_US / 'domestic',
                    'export_opportunities_apply_url': urls.domestic.EXPORT_OPPORTUNITIES,
                    'is_profile_published': company['is_published_find_a_supplier'] if company else False,
                    'FAB_BUSINESS_PROFILE_URL': self.get_business_profile_url(),
                    'FEATURE_ADMIN_REQUESTS_ON': settings.FEATURE_FLAGS['ADMIN_REQUESTS_ON'],
                }
            )
            if company:
                context['has_admin_request'] = helpers.has_editor_admin_request(
                    sso_session_id=self.request.user.session_id, sso_id=self.request.user.id
                )

        return context


class BaseFormView(FormView):

    success_url = reverse_lazy('business-profile')

    def get_initial(self):
        return self.request.user.company.serialize_for_form()

    def form_valid(self, form):
        try:
            response = api_client.company.profile_update(
                sso_session_id=self.request.user.session_id, data=self.serialize_form(form)
            )
            response.raise_for_status()
        except RequestException:
            self.send_update_error_to_sentry(user=self.request.user, api_response=response)
            raise
        else:
            if self.success_message:
                messages.success(self.request, self.success_message)
            return redirect(self.success_url)

    def serialize_form(self, form):
        return form.cleaned_data

    @staticmethod
    def send_update_error_to_sentry(user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending
        sentry_sdk.set_user({'hashed_uuid': user.hashed_uuid, 'user_email': user.email})
        sentry_sdk.set_extra('api_response', str(api_response.content))
        sentry_sdk.capture_message('Updating company profile failed')


class SocialLinksFormView(BaseFormView):
    template_name = 'business_profile/social-links-form.html'
    form_class = forms.SocialLinksForm
    success_message = 'Social links updated'


class EmailAddressFormView(BaseFormView):
    template_name = 'business_profile/email-address-form.html'
    form_class = forms.EmailAddressForm
    success_message = 'Email address updated'


class DescriptionFormView(BaseFormView):
    form_class = forms.DescriptionForm
    template_name = 'business_profile/description-form.html'
    success_message = 'Description updated'


class WebsiteFormView(BaseFormView):
    form_class = forms.WebsiteForm
    template_name = 'business_profile/website-form.html'
    success_message = 'Website updated'


class LogoFormView(BaseFormView):
    def get_initial(self):
        return {}

    form_class = forms.LogoForm
    template_name = 'business_profile/logo-form.html'
    success_message = 'Logo updated'


class ExpertiseRoutingFormView(FormView):

    form_class = forms.ExpertiseRoutingForm
    template_name = 'business_profile/expertise-routing-form.html'

    def form_valid(self, form):
        if form.cleaned_data['choice'] == form.REGION:
            url = reverse('business-profile-expertise-regional')
        elif form.cleaned_data['choice'] == form.COUNTRY:
            url = reverse('business-profile-expertise-countries')
        elif form.cleaned_data['choice'] == form.INDUSTRY:
            url = reverse('business-profile-expertise-industries')
        elif form.cleaned_data['choice'] == form.LANGUAGE:
            url = reverse('business-profile-expertise-languages')
        else:
            raise NotImplementedError
        return redirect(url)

    def get_context_data(self, **kwargs):
        company = self.request.user.company.serialize_for_template()
        return super().get_context_data(company=company, **kwargs)


class RegionalExpertiseFormView(BaseFormView):
    form_class = forms.RegionalExpertiseForm
    template_name = 'business_profile/expertise-regions-form.html'
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-routing')


class CountryExpertiseFormView(BaseFormView):
    form_class = forms.CountryExpertiseForm
    template_name = 'business_profile/expertise-countries-form.html'
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-routing')


class IndustryExpertiseFormView(BaseFormView):
    form_class = forms.IndustryExpertiseForm
    template_name = 'business_profile/expertise-industry-form.html'
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-routing')


class LanguageExpertiseFormView(BaseFormView):
    form_class = forms.LanguageExpertiseForm
    template_name = 'business_profile/expertise-language-form.html'
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-routing')


class BusinessDetailsFormView(BaseFormView):
    template_name = 'business_profile/business-details-form.html'

    def get_form_class(self):
        if self.request.user.company.is_in_companies_house:
            return forms.CompaniesHouseBusinessDetailsForm
        return forms.NonCompaniesHouseBusinessDetailsForm

    success_message = 'Business details updated'


class PublishFormView(BaseFormView):
    form_class = forms.PublishForm
    template_name = 'business_profile/business-profile-publish.html'
    success_url = reverse_lazy('business-profile')
    success_message = 'Published status successfully changed'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.company.is_publishable:
            return redirect('business-profile')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'company': self.request.user.company.serialize_for_form()}

    def get_context_data(self, **kwargs):
        company = self.request.user.company.serialize_for_template()
        return super().get_context_data(company=company, **kwargs)


class BaseCaseStudyWizardView(NamedUrlSessionWizardView):

    done_step_name = 'finished'

    file_storage = DefaultStorage()

    form_list = ((BASIC, forms.CaseStudyBasicInfoForm), (MEDIA, forms.CaseStudyRichMediaForm))
    templates = {
        BASIC: 'business_profile/case-study-basic-form.html',
        MEDIA: 'business_profile/case-study-media-form.html',
    }

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        # the case studies edit view pre-populates the image fields with the
        # url of the existing value (rather than the real file). Things would
        # get confused if we send a string instead of a file here.
        for field in ['image_one', 'image_two', 'image_three']:
            value = data.get(field)
            if not value or isinstance(value, str):
                del data[field]
        return data


class CaseStudyWizardEditView(BaseCaseStudyWizardView):
    def get_form_initial(self, step):
        response = api_client.company.case_study_retrieve(
            sso_session_id=self.request.user.session_id, case_study_id=self.kwargs['id']
        )
        if response.status_code == 404:
            raise Http404()
        response.raise_for_status()
        return response.json()

    def done(self, form_list, *args, **kwags):
        response = api_client.company.case_study_update(
            data=self.serialize_form_list(form_list),
            case_study_id=self.kwargs['id'],
            sso_session_id=self.request.user.session_id,
        )
        response.raise_for_status()
        return redirect('business-profile')

    def get_step_url(self, step):
        return reverse(self.url_name, kwargs={'step': step, 'id': self.kwargs['id']})


class CaseStudyWizardCreateView(BaseCaseStudyWizardView):
    def done(self, form_list, *args, **kwags):
        response = api_client.company.case_study_create(
            sso_session_id=self.request.user.session_id, data=self.serialize_form_list(form_list)
        )
        response.raise_for_status()
        return redirect('business-profile')


class ManageCollaborationRequestMixin:
    form_class = forms.AdminCollaborationRequestManageForm
    success_url = reverse_lazy('business-profile-admin-tools')

    def form_valid(self, form):
        if form.cleaned_data['action'] == form.DELETE:
            helpers.collaboration_request_delete(
                sso_session_id=self.request.user.session_id, request_key=form.cleaned_data['request_key']
            )
        elif form.cleaned_data['action'] == form.APPROVE:
            helpers.collaboration_request_accept(
                sso_session_id=self.request.user.session_id, request_key=form.cleaned_data['request_key']
            )
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        if cleaned_data['action'] == self.form_class.DELETE:
            success_message = 'Request successfully deleted'
        elif cleaned_data['action'] == self.form_class.APPROVE:
            success_message = 'Collaborator added'
        else:
            raise NotImplementedError
        return success_message


class AdminCollaboratorsListView(ManageCollaborationRequestMixin, SuccessMessageMixin, FormView):
    template_name = 'business_profile/admin-collaborator-list.html'

    def get_context_data(self, **kwargs):
        collaborators = helpers.collaborator_list(self.request.user.session_id)
        requests = helpers.collaboration_request_list(self.request.user.session_id)
        requests = [c for c in requests if not c['accepted']]
        return super().get_context_data(collaborators=collaborators, collaboration_requests=requests, **kwargs)


class MemberDisconnectFromCompany(DisconnectFromCompanyMixin, SuccessMessageMixin, FormView):
    template_name = 'business_profile/disconnect-from-company.html'

    def get_context_data(self, **kwargs):
        company = self.request.user.company.serialize_for_form()
        return super().get_context_data(company=company, **kwargs)


class AdminCollaboratorEditFormView(SuccessMessageMixin, FormView):
    template_name = 'business_profile/admin-collaborator-edit.html'
    form_class = forms.AdminCollaboratorEditForm
    success_url = reverse_lazy('business-profile-admin-tools')

    success_messages = {
        forms.REMOVE_COLLABORATOR: 'Collaborator removed',
        forms.CHANGE_COLLABORATOR_TO_MEMBER: 'Collaborator role changed to Member',
        forms.CHANGE_COLLABORATOR_TO_ADMIN: 'Collaborator role changed to Admin',
    }

    def dispatch(self, *args, **kwargs):
        if not self.collaborator:
            raise Http404()
        if self.collaborator['sso_id'] == self.request.user.id:
            return redirect(self.success_url)
        return super().dispatch(*args, **kwargs)

    @cached_property
    def collaborator(self):
        return helpers.retrieve_collaborator(
            sso_session_id=self.request.user.session_id, collaborator_sso_id=int(self.kwargs['sso_id'])
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(collaborator=self.collaborator, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        return {**kwargs, 'current_role': self.collaborator['role']}

    def form_valid(self, form):
        action = form.cleaned_data['action']
        if action == forms.REMOVE_COLLABORATOR:
            helpers.remove_collaborator(sso_session_id=self.request.user.session_id, sso_id=self.collaborator['sso_id'])
        else:
            role = {
                forms.CHANGE_COLLABORATOR_TO_MEMBER: user_roles.MEMBER,
                forms.CHANGE_COLLABORATOR_TO_ADMIN: user_roles.ADMIN,
            }[action]
            helpers.collaborator_role_update(
                sso_session_id=self.request.user.session_id, sso_id=self.collaborator['sso_id'], role=role
            )
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_messages[cleaned_data['action']]


class AdminDisconnectFormView(DisconnectFromCompanyMixin, SuccessMessageMixin, FormView):
    template_name = 'business_profile/admin-disconnect.html'

    def get_context_data(self, **kwargs):
        is_sole_admin = helpers.is_sole_admin(self.request.user.session_id)
        return super().get_context_data(is_sole_admin=is_sole_admin, **kwargs)


class AdminInviteNewAdminFormView(SuccessMessageMixin, FormView):
    template_name = 'business_profile/admin-invite-admin.html'
    form_class = forms.AdminInviteNewAdminForm
    success_url = reverse_lazy('business-profile-admin-tools')

    def get_success_message(self, cleaned_data):
        if cleaned_data['collaborator_email']:
            success_message = (
                'We have sent an invite to %(collaborator_email)s to become the new administrator for the business '
                'profile. You will be notified when this happens.'
            )
        else:
            success_message = 'Collaborator role changed to Admin'
        return success_message % cleaned_data

    @cached_property
    def collaborators(self):
        return helpers.collaborator_list(self.request.user.session_id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['collaborator_choices'] = [
            (item['sso_id'], item['name'] or item['company_email'])
            for item in self.collaborators
            if item['role'] != user_roles.ADMIN
        ]
        return kwargs

    def get_context_data(self, **kwargs):
        has_collaborators = len(self.collaborators) > 1
        return super().get_context_data(has_collaborators=has_collaborators, **kwargs)

    def form_valid(self, form):
        try:
            if form.cleaned_data['collaborator_email']:
                helpers.collaborator_invite_create(
                    sso_session_id=self.request.user.session_id,
                    collaborator_email=form.cleaned_data['collaborator_email'],
                    role=user_roles.ADMIN,
                )
            else:
                helpers.collaborator_role_update(
                    sso_session_id=self.request.user.session_id,
                    sso_id=form.cleaned_data['sso_id'],
                    role=user_roles.ADMIN,
                )
        except HTTPError as error:
            if error.response.status_code == 400:
                parsed = error.response.json()
                if 'collaborator_email' in parsed:
                    parsed = parsed['collaborator_email']
                form.add_error(field=None, error=parsed)
                return self.form_invalid(form)
            else:
                raise
        return super().form_valid(form)


class AdminInviteCollaboratorFormView(SuccessMessageMixin, FormView):
    template_name = 'business_profile/admin-invite-collaborator.html'
    form_class = forms.AdminInviteCollaboratorForm
    success_message = (
        'We have sent a confirmation to %(collaborator_email)s with an invitation to become a collaborator'
    )
    success_url = reverse_lazy('business-profile-admin-invite-collaborator')

    def get_context_data(self, **kwargs):
        collaborator_invites = helpers.collaborator_invite_list(self.request.user.session_id)
        collaborator_invites_not_accepted = [c for c in collaborator_invites if not c['accepted']]
        return super().get_context_data(collaborator_invites=collaborator_invites_not_accepted, **kwargs)

    def form_valid(self, form):
        try:
            helpers.collaborator_invite_create(
                sso_session_id=self.request.user.session_id,
                collaborator_email=form.cleaned_data['collaborator_email'],
                role=form.cleaned_data['role'],
            )
        except HTTPError as error:
            if error.response.status_code == 400:
                form.add_error(field=None, error=error.response.json())
                return self.form_invalid(form)
            else:
                raise
        return super().form_valid(form)


class AdminInviteCollaboratorDeleteFormView(SuccessMessageMixin, FormView):
    form_class = forms.AdminInviteCollaboratorDeleteForm
    success_message = 'Invitation successfully deleted'
    success_url = reverse_lazy('business-profile-admin-invite-collaborator')

    def form_valid(self, form):
        helpers.collaborator_invite_delete(
            sso_session_id=self.request.user.session_id, invite_key=form.cleaned_data['invite_key']
        )
        return super().form_valid(form)


class ProductsServicesRoutingFormView(FormView):

    form_class = forms.ExpertiseProductsServicesRoutingForm
    template_name = 'business_profile/products-services-routing-form.html'

    def form_valid(self, form):
        url = reverse('business-profile-expertise-products-services', kwargs={'category': form.cleaned_data['choice']})
        return redirect(url)

    def get_context_data(self, **kwargs):
        return super().get_context_data(company=self.request.user.company.serialize_for_template(), **kwargs)


class ProductsServicesFormView(BaseFormView):
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-products-services-routing')
    field_name = 'expertise_products_services'

    def dispatch(self, *args, **kwargs):
        form = forms.ExpertiseProductsServicesRoutingForm(data={'choice': self.kwargs['category']})
        if not form.is_valid():
            return redirect(self.success_url)
        return super().dispatch(*args, **kwargs)

    form_class = forms.ExpertiseProductsServicesForm
    template_name = 'business_profile/products-services-form.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(category=self.kwargs['category'].replace('-', ' '), **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.kwargs['category']
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        value = initial[self.field_name].get(self.kwargs['category'], [])
        return {self.field_name: '|'.join(value)}

    def serialize_form(self, form):
        return {
            self.field_name: {
                **self.request.user.company.data[self.field_name],
                self.kwargs['category']: form.cleaned_data[self.field_name],
            }
        }


class ProductsServicesOtherFormView(BaseFormView):
    success_message = None
    success_url = reverse_lazy('business-profile-expertise-products-services-routing')
    field_name = 'expertise_products_services'
    form_class = forms.ExpertiseProductsServicesOtherForm
    template_name = 'business_profile/products-services-other-form.html'

    def get_initial(self):
        initial = super().get_initial()
        value = initial[self.field_name].get('other', [])
        return {self.field_name: ', '.join(value)}

    def serialize_form(self, form):
        return {
            self.field_name: {
                **self.request.user.company.data[self.field_name],
                'other': form.cleaned_data[self.field_name],
            }
        }


class PersonalDetailsFormView(core.mixins.CreateUpdateUserProfileMixin, SuccessMessageMixin, FormView):
    template_name = 'business_profile/personal-details-form.html'
    form_class = core.forms.PersonalDetails
    success_url = reverse_lazy('business-profile')
    success_message = 'Details updated'

    def form_valid(self, form):
        self.create_update_user_profile(form)
        return super().form_valid(form)


class IdentityVerificationRequestFormView(SuccessMessageMixin, FormView):
    template_name = 'business_profile/request-verify.html'
    form_class = forms.NoOperationForm
    success_url = reverse_lazy('business-profile')
    success_message = 'Request to verify sent'

    def dispatch(self, *args, **kwargs):
        if self.request.user.company.is_identity_check_message_sent:
            return redirect(self.success_url)
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        response = api_client.company.verify_identity_request(self.request.user.session_id)
        response.raise_for_status()
        return super().form_valid(form)
