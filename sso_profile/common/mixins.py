from sso_profile.common import helpers


class PreventCaptchaRevalidationMixin:
    """When get_all_cleaned_data() is called the forms are revalidated,
    which causes captcha to fail becuase the same captcha response from google
    is posted to google multiple times. This captcha response is a nonce, and
    so google complains the second time it's seen.

    This is worked around by removing captcha from the form before the view
    calls get_all_cleaned_data

    NB: this 'looks' like it can be swapped out for the version in core.mixins
    but doing so without a further refactor to the views results in an infinite
    redirect loop, so be aware that it's not necessarily a quick win.
    """

    @property
    def captcha_step_index(self):
        for step_name, form_class in self.get_form_list().items():
            if 'captcha' in form_class.base_fields:
                return self.get_step_index(step_name)
        # this can happen if the step with a captcha is optional
        return -1

    def get_form(self, step=None, *args, **kwargs):
        form = super().get_form(step=step, *args, **kwargs)
        fields = form.fields
        if 'captcha' in fields and self.steps.index and self.steps.index > self.captcha_step_index:
            del fields['captcha']
        return form


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
