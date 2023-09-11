from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from config.celery import app
from export_academy.models import Event, send_notifications_for_all_bookings


@app.task
def send_automated_events_notification():
    time_delay = settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES
    events = Event.objects.filter(
        start_date__gte=timezone.now() + timedelta(minutes=time_delay * 2),
        start_date__lt=timezone.now() + timedelta(minutes=time_delay * 3),
    )

    for event in events:
        current_timezone = timezone.get_current_timezone()
        event_start_date = event.start_date.astimezone(current_timezone)
        event_end_date = event.end_date.astimezone(current_timezone)
        event_time = f'{event_start_date.strftime("%H:%M")} - {event_end_date.strftime("%H:%M")}'
        additional_notify_data = dict(
            event_date=event.start_date.strftime('%-d %B %Y'),
            event_time=event_time,
        )
        send_notifications_for_all_bookings(
            event,
            settings.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID,
            additional_notify_data,
        )


@app.task
def remove_past_events_media():
    time_delay = settings.EXPORT_ACADEMY_REMOVE_EVENT_MEDIA_AFTER_DAYS
    events = Event.objects.filter(
        start_date__lt=timezone.now() - timedelta(days=time_delay),
        start_date__gte=timezone.now() - timedelta(days=time_delay * 2),
    )
    for event in events:
        if event.completed and event.video_recording:
            event.video_recording = None
            event.save()
