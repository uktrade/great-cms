from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView

from export_academy import helpers, models
from export_academy.forms import EARegistration
from export_academy.models import Registration


class EventListView(ListView):
    model = models.Event


class RegistrationFormView(FormView):
    template_name = 'export_academy/registration_form.html'
    form_class = EARegistration
    success_url = reverse_lazy('export_academy:registration-success')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user_email = self.request.user.email
        self.request.session['user_email'] = user_email
        reg = Registration(
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


class RegistrationSuccessPageView(TemplateView):
    template_name = 'export_academy/registration_form_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('export_academy:upcoming-events'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_email'] = self.request.session.get('user_email')
        return super().get_context_data(**kwargs)


class BookingSuccessPageView(TemplateView):
    template_name = 'export_academy/booking_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('export_academy:upcoming-events'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_email'] = self.request.session.get('user_email')
        return super().get_context_data(**kwargs)
