from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

import sso_profile.common.mixins
from sso_profile.personal_profile import forms


class PersonalProfileEditFormView(
    sso_profile.common.mixins.CreateUpdateUserProfileMixin, SuccessMessageMixin, FormView
):
    template_name = 'personal_profile/personal-profile-edit-form.html'
    form_class = forms.PersonalProfileEdit
    success_url = reverse_lazy('sso_profile:personal-profile:display')
    success_message = 'Personal details updated'

    def get_initial(self):
        return {
            'given_name': self.request.user.first_name,
            'family_name': self.request.user.last_name,
            'job_title': self.request.user.job_title,
            'phone_number': self.request.user.mobile_phone_number,
        }

    def form_valid(self, form):
        self.create_update_user_profile(form)
        return super().form_valid(form)


class PersonalProfileView(TemplateView):
    template_name = 'personal_profile/personal-profile.html'
