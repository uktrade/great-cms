from uuid import uuid4

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.text import get_valid_filename
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView
from icalendar import Calendar, Event
from rest_framework.generics import GenericAPIView

from config import settings
from core import mixins as core_mixins
from export_academy import filters, forms, helpers, models
from export_academy.helpers import get_buttons_for_event
from export_academy.mixins import BookingMixin
from export_academy.models import ExportAcademyHomePage


class EventListView(
    core_mixins.GetSnippetContentMixin,
    FilterView,
    ListView,
):
    model = models.Event
    queryset = model.upcoming
    filterset_class = filters.EventFilter
    template_name = 'export_academy/event_list.html'
    paginate_by = 10

    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event)

    def get(self, request, *args, **kwargs):
        request.GET = helpers.build_request_navigation_params(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = ExportAcademyHomePage.objects.first()
        return ctx


class BookingUpdateView(BookingMixin, UpdateView):
    booking_model = models.Booking
    success_url = reverse_lazy('export_academy:booking-success')
    fields = ['status']
    notify_template = None

    def get_object(self, queryset=None):
        post_data = self.request.POST
        booking_object = self.register_booking(post_data)
        self.send_email_confirmation(booking_object, post_data)
        return booking_object


class RegistrationFormView(BookingMixin, FormView):
    template_name = 'export_academy/registration_form.html'
    form_class = forms.EARegistration
    success_url = reverse_lazy('export_academy:registration-success')
    model = models.Registration
    booking_model = models.Booking
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID

    def save_registration(self, form):
        cleaned_data = form.cleaned_data
        reg_data = dict(
            first_name=cleaned_data.get('first_name'),
            last_name=cleaned_data.get('last_name'),
            email=self.request.user.email,  # type: ignore
            data=cleaned_data,
        )
        self.save_model(reg_data)

    def confirm_booking(self, booking_id):
        booking_data = dict(event_id=booking_id, status=models.Booking.CONFIRMED)
        booking_object = self.register_booking(booking_data)
        self.send_email_confirmation(booking_object, booking_data)

    def form_valid(self, form):
        self.save_registration(form)
        self.send_gov_notify(form.cleaned_data)
        booking_id = self.kwargs.get('booking_id')
        self.confirm_booking(booking_id)
        return super().form_valid(form)


class SuccessPageView(TemplateView):
    pass


class EventDetailsView(DetailView):
    template_name = 'export_academy/event_details.html'
    model = models.Event

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # video_render tag which helps in adding subtitles
        # needs input in specific way as below
        event: models.Event = kwargs.get('object', {})
        video = event.video_recording
        ctx.update(event_video={'video': video})

        return ctx


class DownloadCalendarView(GenericAPIView):
    event_model = models.Event

    def post(self, request, *args, **kwargs):
        post_data = self.request.POST
        event_id = post_data['event_id']
        event = self.event_model.objects.get(id=event_id)
        cal = Calendar()
        cal.add('PRODID', '-//Export academy events//')
        cal.add('VERSION', '1.0')
        meeting = Event()
        meeting.add('SUMMARY', event.name)
        meeting.add('DTSTART', event.start_date)
        meeting.add('DTEND', event.end_date)
        meeting['LOCATION'] = reverse_lazy('export_academy:upcoming-events')
        meeting.add('DESCRIPTION', event.description)
        meeting['UID'] = uuid4()
        file_name = get_valid_filename(event.name)

        cal.add_component(meeting)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'inline; filename={file_name}.ics'
        return response
