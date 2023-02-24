from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView, UpdateView
from django_filters.views import FilterView

from export_academy import filters, forms, helpers, models


class EventListView(FilterView, ListView):
    model = models.Event
    filterset_class = filters.EventFilter
    template_name = 'export_academy/event_list.html'

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


class BookingUpdateView(UpdateView):
    model = models.Booking
    success_url = reverse_lazy('export_academy:booking-success')
    fields = ['status']

    def get_object(self, queryset=None):
        data = self.request.POST
        obj, _created = self.model.objects.get_or_create(
            event_id=data['event_id'], registration_id=self.request.user.email, defaults={'status': data['status']}
        )

        return obj


class RegistrationFormView(FormView):
    template_name = 'export_academy/registration_form.html'
    form_class = forms.EARegistration
    success_url = reverse_lazy('export_academy:registration-success')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user_email = self.request.user.email

        reg = models.Registration(
            first_name=cleaned_data.get('first_name'),
            last_name=cleaned_data.get('last_name'),
            email=user_email,
            data=cleaned_data,
        )
        reg.save()
        helpers.notify_registration(
            email_data={
                'business_name': cleaned_data['business_name'],
                'first_name': cleaned_data['first_name'],
            },
            form_url=self.request.path,
            email_address=user_email,
        )
        return super().form_valid(form)


class SuccessPageView(TemplateView):
    pass
