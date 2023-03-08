from datetime import datetime, timedelta, timezone

from directory_forms_api_client import actions
from django.conf import settings

from config.celery import app
from export_academy.models import Booking, Event


def send_notifications_for_all_bookings(event, template_id, additional_notify_data=None):
    bookings = Booking.objects.filter(event_id=event.id)
    for booking in bookings:
        email = booking.registration.email

        action = actions.GovNotifyEmailAction(
            email_address=email,
            template_id=template_id,
            form_url=str(),
        )
        notify_data = dict(first_name=booking.registration.first_name, event_name=booking.event.name)
        if additional_notify_data:
            notify_data.update(**additional_notify_data)

        action.save(notify_data)


@app.task
def send_automated_events_notification():
    time_delay = settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES
    events = Event.objects.filter(
        start_date__gte=datetime.now(timezone.utc) + timedelta(minutes=time_delay),
        start_date__lt=datetime.now(timezone.utc) + timedelta(minutes=time_delay * 2),
    )

    for event in events:
        event_time = f'{event.start_date.strftime("%H:%M")} - {event.end_date.strftime("%H:%M")}'
        additional_notify_data = dict(
            event_date=event.start_date.strftime('%-d %B %Y'),
            event_time=event_time,
        )
        send_notifications_for_all_bookings(
            event,
            settings.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID,
            additional_notify_data,
        )
