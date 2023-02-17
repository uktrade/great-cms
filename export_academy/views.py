from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from config import settings
from export_academy import forms, models
from export_academy.mixins import SaveAndSendNotifyMixin


class EventListView(ListView):
    model = models.Event

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        bookings = []

        if user.is_authenticated:
            bookings = models.Booking.objects.filter(registration_id=user.email, status='Confirmed').values_list(
                'event_id', flat=True
            )

        ctx.update(bookings=bookings)

        return ctx


class BookingUpdateView(SaveAndSendNotifyMixin, UpdateView):
    model = models.Booking
    success_url = reverse_lazy('export_academy:booking-success')
    fields = ['status']
    notify_template = None

    def register_booking(self, data):
        booking_data = dict(
            event_id=data['event_id'], registration_id=self.request.user.email, defaults={'status': data['status']}
        )
        booking_object, _created = self.get_or_save_object(booking_data)
        return booking_object

    def send_email_confirmation(self, booking_object: models.Booking, post_data):
        if post_data['status'] == booking_object.CONFIRMED:
            self.notify_template = settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID
        else:
            self.notify_template = settings.EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID

        notify_data = dict(first_name=booking_object.registration.first_name, event_names=booking_object.event.name)
        self.send_gov_notify(notify_data)

    def get_object(self, queryset=None):
        post_data = self.request.POST
        booking_object = self.register_booking(post_data)
        self.send_email_confirmation(booking_object, post_data)
        return booking_object


class RegistrationFormView(SaveAndSendNotifyMixin, FormView):
    template_name = 'export_academy/registration_form.html'
    form_class = forms.EARegistration
    success_url = reverse_lazy('export_academy:registration-success')
    model = models.Registration
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID

    def save_registration(self, form):
        cleaned_data = form.cleaned_data
        reg_data = dict(
            first_name=cleaned_data.get('first_name'),
            last_name=cleaned_data.get('last_name'),
            email=self.request.user.email,
            data=cleaned_data,
        )
        self.save_model(reg_data)

    def form_valid(self, form):
        self.save_registration(form)
        self.send_gov_notify(form.cleaned_data)
        return super().form_valid(form)


class SuccessPageView(TemplateView):
    pass
