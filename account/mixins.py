from django.utils.functional import cached_property

from core import helpers

class CreateUpdateUserProfileMixin:
    def serialize_user_profile(self, form):
        return {
            'first_name': form.cleaned_data['given_name'],
            'last_name': form.cleaned_data['family_name'],
            'job_title': form.cleaned_data.get('job_title'),
            'mobile_phone_number': form.cleaned_data.get('phone_number'),
        }

    def create_update_user_profile(self, form):
        data = self.serialize_user_profile(form)
        if self.request.user.has_user_profile:
            helpers.update_user_profile(
                sso_session_id=self.request.user.session_id, data=self.serialize_user_profile(form)
            )
        else:
            helpers.create_user_profile(sso_session_id=self.request.user.session_id, data=data)

        self.request.user.first_name = data['first_name']
        self.request.user.last_name = data['last_name']