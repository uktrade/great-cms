import logging
from datetime import timedelta
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
from drf_spectacular.utils import extend_schema
from great_components.mixins import GA360Mixin
from icalendar import Alarm, Calendar, Event
from rest_framework.generics import GenericAPIView

from config import settings
from core import mixins as core_mixins
from core.templatetags.content_tags import format_timedelta
from export_academy import filters, forms, models
from export_academy.helpers import (
    calender_content,
    get_badges_for_event,
    get_buttons_for_event,
)
from export_academy.mixins import BookingMixin, RegistrationMixin
from export_academy.models import ExportAcademyHomePage, Registration

logger = logging.getLogger(__name__)


class EventListView(GA360Mixin, core_mixins.GetSnippetContentMixin, FilterView, ListView):
    model = models.Event
    queryset = model.upcoming
    filterset_class = filters.EventFilter
    template_name = 'export_academy/event_list.html'
    paginate_by = 10

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(  # from GA360Mixin
            page_id='MagnaPage',
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section='export-academy',
            site_subsection='events',
        )

    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event)

    def get_badges_for_event(self, event):
        user = self.request.user
        return get_badges_for_event(user, event)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()
        return ctx


class BookingUpdateView(BookingMixin, UpdateView):
    booking_model = models.Booking
    fields = ['status']
    notify_template = None

    def get_object(self, queryset=None):
        post_data = self.request.POST
        booking_object = self.register_booking(post_data)
        self.send_email_confirmation(booking_object, post_data)
        return booking_object

    def get_success_url(self):
        success_url = (
            'export_academy:cancellation-success' if self.object.is_cancelled else 'export_academy:booking-success'
        )
        return reverse_lazy(success_url, kwargs={'booking_id': self.object.id})


class SuccessPageView(core_mixins.GetSnippetContentMixin, TemplateView):
    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event, on_confirmation=True)

    def user_just_registered(self, booking):
        return self.request.path == reverse_lazy(
            'export_academy:registration-success', kwargs={'booking_id': booking.id}
        )

    def user_editing_registration(self):
        return self.request.path == reverse_lazy('export_academy:registration-edit-success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()

        editing_registration = self.user_editing_registration()

        if editing_registration:
            ctx['heading'] = 'Registration update'
            ctx['editing_registration'] = editing_registration
            ctx['current_page_breadcrumb'] = 'Registration'
            return ctx

        booking = models.Booking.objects.get(id=ctx['booking_id'])
        if self.user_just_registered(booking):
            ctx['heading'] = 'Registration'
        elif booking.status == 'Confirmed':
            ctx['heading'] = 'Booking'
        else:
            ctx['heading'] = 'Cancellation'

        ctx['booking'] = booking
        ctx['event'] = booking.event

        just_registered = self.user_just_registered(booking)
        ctx['just_registered'] = just_registered
        ctx['current_page_breadcrumb'] = 'Registration' if just_registered else 'Events'
        return ctx


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
        ctx['video_duration'] = format_timedelta(timedelta(seconds=event.video_recording.duration))

        return ctx


@extend_schema(exclude=True)
class DownloadCalendarView(GenericAPIView):
    event_model = models.Event

    def post(self, request, *args, **kwargs):
        post_data = self.request.POST
        event_id = post_data['event_id']
        event = self.event_model.objects.get(id=event_id)

        cal = Calendar()
        cal.add('PRODID', '-//Export academy events//')
        cal.add('VERSION', '2.0')
        meeting = Event()
        meeting.add('SUMMARY', f'UK Export Academy event - {event.name}')
        meeting.add('DTSTART', event.start_date)
        meeting.add('DTEND', event.end_date)
        meeting['LOCATION'] = event.location if event.format == event.IN_PERSON else 'MS Teams'
        meeting['UID'] = uuid4()

        description = f'{event.name}\n\n{event.description}{calender_content()}'
        meeting.add('DESCRIPTION', description)

        file_name = get_valid_filename(event.name)
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')

        alert_time = timedelta(minutes=-15)
        alarm.add('trigger', alert_time)
        meeting.add_component(alarm)

        cal.add_component(meeting)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'inline; filename={file_name}.ics'
        return response


class RegistrationPersonalDetails(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.PersonalDetails
    model = models.Registration
    template_name = 'export_academy/registration_form.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:upcoming-events'
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
        return super().get_context_data(
            **kwargs,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 1 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About you',
            email=self.request.user.email,
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-experience')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationExportExperience(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.ExportExperience
    model = models.Registration
    template_name = 'export_academy/registration_form.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-details'
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
        return super().get_context_data(
            **kwargs,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 2 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About your export experience',
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-business')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationBusinessDetails(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.BusinessDetails
    model = models.Registration
    template_name = 'export_academy/registration_form.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-experience'
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
        return super().get_context_data(
            **kwargs,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 3 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About your business',
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-marketing')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationMarketingSources(
    core_mixins.GetSnippetContentMixin,
    RegistrationMixin,
    FormView,
):
    form_class = forms.MarketingSources
    model = models.Registration
    template_name = 'export_academy/registration_form.html'
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-business'
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
        return super().get_context_data(
            **kwargs,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 4 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='And finally...',
        )

    def get_success_url(self):
        return reverse_lazy('export_academy:registration-confirm')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationConfirmChoices(core_mixins.GetSnippetContentMixin, BookingMixin, RegistrationMixin, FormView):
    template_name = 'export_academy/registration_form_confirm.html'
    model = models.Registration
    booking_model = models.Booking
    form_class = forms.RegistrationConfirm
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID
    booking_id = ''

    def submit_registration(self):
        reg_data = {
            'email': self.request.user.email,
            'first_name': self.initial_data['first_name'],
            'last_name': self.initial_data['last_name'],
            'data': self.initial_data,
        }

        if Registration.objects.filter(email=self.request.user.email).exists():
            registration = Registration.objects.get(email=self.request.user.email)
            registration.__dict__.update(**reg_data)
            registration.save()
            return

        self.model(**reg_data).save()
        self.send_gov_notify(self.initial_data)

    def confirm_booking(self, event_id):
        booking_data = dict(event_id=event_id, status=models.Booking.CONFIRMED)
        booking_object = self.register_booking(booking_data)
        del self.request.session['event_id']
        self.booking_id = booking_object.id
        self.send_email_confirmation(booking_object, booking_data)

    def form_valid(self, form):
        self.submit_registration()
        event_id = self.request.session.get('event_id')
        if event_id is not None:
            self.confirm_booking(event_id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        self.get_initial()
        return super().get_context_data(
            **kwargs,
            back_url='export_academy:registration-marketing',
            landing_page=ExportAcademyHomePage.objects.first(),
            form_data=self.initial_data,
            email=self.request.user.email,
        )

    def get_success_url(self):
        if self.booking_id != '':
            return reverse_lazy('export_academy:registration-success', kwargs={'booking_id': self.booking_id})
        return reverse_lazy('export_academy:registration-edit-success')
