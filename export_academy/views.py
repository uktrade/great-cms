from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from contact.views import BaseNotifyFormView
from export_academy import helpers, models
from export_academy.forms import EARegistration


class EventListView(ListView):
    model = models.Event


class RegistrationFormView(BaseNotifyFormView):
    template_name = 'registration_form.html'
    form_class = EARegistration
    success_url = reverse_lazy('export_academy:registration-success')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user_email = cleaned_data['email']
        self.request.session['user_email'] = user_email
        helpers.notify_registration(
            email_data={
                'business_name': cleaned_data['business_name'],
                'first_name': cleaned_data['full_name'],
            },
            form_url=self.request.path,
            email_address=user_email,
        )
        return super().form_valid(form)


class RegistrationSuccessPageView(TemplateView):
    template_name = 'registration_form_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('export_academy:upcoming-events'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_email'] = self.request.session.get('user_email')
        return super().get_context_data(**kwargs)


class BookingSuccessPageView(TemplateView):
    template_name = 'booking_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('export_academy:upcoming-events'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_email'] = self.request.session.get('user_email')
        return super().get_context_data(**kwargs)
