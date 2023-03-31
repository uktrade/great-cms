from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from storages.backends.s3boto3 import S3Boto3Storage

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


class SignedURLView(GenericAPIView):
    storage: S3Boto3Storage = default_storage

    def post(self, request, *args, **kwargs):
        client = self.storage.connection.meta.client
        request_file_name = request.data.get('fileName', get_random_string(7))
        qualified_key = f'media/{request_file_name}'
        key = self.storage.get_available_name(qualified_key)

        url = client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.storage.bucket.name,
                'Key': key,
            },
            ExpiresIn=3600,
        )
        return Response({'url': url})
