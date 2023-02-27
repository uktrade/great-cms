from directory_forms_api_client import actions
from directory_forms_api_client.forms import GovNotifyEmailActionMixin

from config import settings
from export_academy import models

# class SaveAndSendNotifyMixin(GovNotifyEmailActionMixin):
#     def save(self, form):
#         user_email = self.request.user.email
#         super(GovNotifyEmailActionMixin, self).save(
#             template_id=self.notify_template,
#             email_address=user_email,
#             form_url=self.request.get_full_path(),
#         )
#         return super(SaveAndSendNotifyMixin, self).save()
#
#     def save_registration(self, data):
#         self.model.save(data)


class SaveAndSendNotifyMixin(GovNotifyEmailActionMixin):
    def save_model(self, data):
        self.model(**data).save()

    def get_or_save_object(self, data):
        return self.model.objects.get_or_create(**data)

    def send_gov_notify(self, data):
        action = actions.GovNotifyEmailAction(
            email_address=self.request.user.email,
            template_id=self.notify_template,
            form_url=self.request.get_full_path(),
        )
        response = action.save(data)
        response.raise_for_status()


class ApplyRegistrationMixin:
    def send_gov_notify(self, form):
        user_email = self.request.user.email
        form.save(
            template_id=settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID,
            email_address=user_email,
            form_url=self.request.get_full_path(),
        )

    def save_registration(self, form):
        cleaned_data = form.cleaned_data
        user_email = self.request.user.email
        reg = models.Registration(
            first_name=cleaned_data.get('first_name'),
            last_name=cleaned_data.get('last_name'),
            email=user_email,
            data=cleaned_data,
        )
        reg.save()

    def form_valid(self, form):
        self.save_registration(form)
        self.send_gov_notify(form)
        return super().form_valid(form)
