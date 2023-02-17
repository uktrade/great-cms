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

    def post(self, request, *args, **kwargs):
        # data = self.request.POST

        return super().post(request, *args, **kwargs)


class RegistrationFormView(SaveAndSendNotifyMixin, FormView):
    template_name = 'export_academy/registration_form.html'
    form_class = forms.EARegistration
    success_url = reverse_lazy('export_academy:registration-success')
    model = models.Registration
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user_email = self.request.user.email
        reg_data = dict(
            first_name=cleaned_data.get('first_name'),
            last_name=cleaned_data.get('last_name'),
            email=user_email,
            data=cleaned_data,
        )
        super().save(reg_data)
        super().send_gov_notify(form)
        return super(RegistrationFormView, self).form_valid(form)


class SuccessPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        # context = self.get_context_data(**kwargs)
        return super(SuccessPageView, self).get(request, *args, **kwargs)
