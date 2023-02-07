from directory_forms_api_client import actions

from config import settings


def notify_registration(email_address, email_data, form_url):
    action = actions.GovNotifyEmailAction(
        email_address=email_address,
        template_id=settings.EXPORT_ACADEMY_REGISTRATION_TEMPLATE_ID,
        form_url=form_url,
    )
    response = action.save(email_data)
    response.raise_for_status()
