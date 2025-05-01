from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from config.celery import app
from core.constants import TemplateTagsEnum
from core.helpers import get_template_id
from export_academy.models import Event, send_notifications_for_all_bookings


@app.task
def send_automated_events_notification():
    """
    Sends a reminder to all people booked on an Event that it is starting shortly.
    """

    template_id = get_template_id(TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER.value)

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
            event_url=event.get_absolute_url(),
        )
        send_notifications_for_all_bookings(
            event.id,
            template_id,
            additional_notify_data,
        )


@app.task
def send_automated_event_complete_notification():
    """
    This task looks for all Event that have been marked as completed within the last hour, that have not
    had event complete emails sent for them. It then forwards a bull email request to directory-forms-api to
    send each Event attendee and 'event' complete email.
    """

    # Time delay for completed event - This is to pick up any event marked as complete within X minutes. By default,
    # it is set to 15 mins (three times the task setting of 5 mins, to give is some redundency).
    time_delay = timezone.now() - timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_EVENT_COMPLETE_TIME_DELAY_MINUTES)
    events = Event.objects.filter(completed__isnull=False, completed__gte=time_delay, completed_email_sent=False)

    template_id = settings.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID

    for event in events:
        # POST bulk email submission to directory-forms-api (which will pick up submission and handle sending of emails)
        send_notifications_for_all_bookings(event.id, template_id)

        # Mark Event as having emails sent
        event.completed_email_sent = True
        event.save()


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
