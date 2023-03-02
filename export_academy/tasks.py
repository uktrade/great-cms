from datetime import datetime, timedelta

from directory_forms_api_client import actions
from django.conf import settings

from config.celery import app
from export_academy.models import Booking, Event


@app.task
def send_automated_notification():
    time_delay = settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES
    events = Event.objects.filter(
        start_date__gte=datetime.now() + timedelta(minutes=time_delay),
        start_date__lt=datetime.now() + timedelta(minutes=time_delay * 2),
    )

    for event in events:
        bookings = Booking.objects.filter(event_id=event.id)
        for booking in bookings:
            email = booking.registration.email

            action = actions.GovNotifyEmailAction(
                email_address=email,
                template_id=settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID,
                form_url=str(),
            )
            notify_data = dict(first_name=booking.registration.first_name, event_names=booking.event.name)

            action.save(notify_data)
