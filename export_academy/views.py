from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView, UpdateView
from django_filters.views import FilterView

from config import settings
from export_academy import filters, forms, models
from export_academy.mixins import BookingMixin


class EventListView(FilterView, ListView):
    model = models.Event
    queryset = model.upcoming
    filterset_class = filters.EventFilter
    template_name = 'export_academy/event_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        bookings = []

        if user.is_authenticated:
            bookings = models.Booking.objects.filter(
                registration_id=user.email, status='Confirmed'  # type: ignore
            ).values_list('event_id', flat=True)

        ctx.update(bookings=bookings, filter=self.filterset_class(self.request.GET))

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
