from directory_forms_api_client import actions
from directory_forms_api_client.helpers import Sender
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin  # /PS-IGNORE

from core.helpers import check_url_host_is_safelisted
from international import forms


class ContactView(GA360Mixin, FormView):  # /PS-IGNORE
    form_class = forms.ContactForm
    template_name = 'international/contact.html'
    subject = 'Great.gov.uk International contact form'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Great.gov.uk International',
            site_section='contact',
        )

    def get_back_url(self):
        back_url = '/international/'
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        success_url = reverse_lazy('international:contact') + '?success=true'
        if self.request.GET.get('next'):
            success_url = success_url + '&next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, back_url=self.get_back_url())

    def submit_feedback(self, form):
        cleaned_data = form.cleaned_data
        is_human_submission = 'csrfmiddlewaretoken' not in cleaned_data

        # Return HttpResponseBadRequest() for all requests not made by a human
        if is_human_submission is False:
            return HttpResponseBadRequest()

        if self.request.GET.get('next'):
            cleaned_data['from_url'] = check_url_host_is_safelisted(self.request)

        sender = Sender(
            email_address=cleaned_data['email'],
            country_code=None,
        )

        action = actions.ZendeskAction(
            full_name=cleaned_data['full_name'],
            email_address=cleaned_data['email'],
            subject=self.subject,
            service_name='great',
            form_url=reverse('international:contact'),
            sender=sender,
        )

        response = action.save(cleaned_data)
        response.raise_for_status()

    def form_valid(self, form):
        self.submit_feedback(form)
        return super().form_valid(form)
