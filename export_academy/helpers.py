from directory_forms_api_client import actions

from config import settings
from export_academy.models import Registration


def is_export_academy_registered(user):
    if not user.is_authenticated:
        return False

    return Registration.objects.filter(pk=user.email).exists()


def notify_registration(email_address, email_data, form_url):
    action = actions.GovNotifyEmailAction(
        email_address=email_address,
        template_id=settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save(email_data)
    response.raise_for_status()
