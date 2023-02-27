from directory_forms_api_client import actions
from directory_forms_api_client.forms import GovNotifyEmailActionMixin


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
