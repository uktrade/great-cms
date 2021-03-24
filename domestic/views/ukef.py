from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from contact.views import BaseNotifyFormView
from core.datastructures import NotifySettings
from domestic.forms import UKEFContactForm


class UKEFHomeView(TemplateView):
    template_name = 'domestic/ukef/home_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['trade_finance_bullets'] = [
            'working capital support',
            'bond support',
            'credit insurance',
        ]
        context['project_finance_bullets'] = [
            'UKEF buyer credit guarantees',
            'direct lending',
            'credit and bond insurance',
        ]
        return context


class ContactView(BaseNotifyFormView):
    template_name = 'domestic/ukef/contact_form.html'
    form_class = UKEFContactForm
    success_url = reverse_lazy('domestic:uk-export-contact-success')
    notify_settings = NotifySettings(
        agent_template=settings.UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.UKEF_CONTACT_AGENT_EMAIL_ADDRESS,
        user_template=settings.UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID,
    )

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        self.request.session['user_email'] = user_email
        return super().form_valid(form)


class SuccessPageView(TemplateView):
    template_name = 'domestic/ukef/contact_form_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('domestic:uk-export-contact'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_email'] = self.request.session.get('user_email')
        return super().get_context_data(**kwargs)
