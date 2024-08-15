from directory_forms_api_client import helpers
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from config import settings
from core.helpers import get_sender_ip_address
from international_buy_from_the_uk import forms
from international_online_offer.core.region_sector_helpers import get_sectors_as_string
from international_online_offer.services import get_dbt_sectors


class ContactView(GA360Mixin, FormView):
    form_class = forms.ContactForm
    template_name = 'buy_from_the_uk/contact.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Buy from the UK',
            site_section='contact',
        )

    def get_success_url(self):
        success_url = (
            reverse_lazy('international:contact') + '?success=true' + '&next=' + '/international/buy-from-the-uk'
        )
        return success_url

    def send_agent_email(self, form):
        agent_email = settings.CONTACT_INDUSTRY_AGENT_EMAIL_ADDRESS
        if agent_email:
            sender = helpers.Sender(
                email_address=form.cleaned_data['email_address'],
                country_code=form.cleaned_data['country'],
                ip_address=get_sender_ip_address(self.request),
            )
            spam_control = helpers.SpamControl(contents=[form.cleaned_data['body']])
            response = form.save(
                form_url=self.request.path,
                email_address=settings.CONTACT_INDUSTRY_AGENT_EMAIL_ADDRESS,
                template_id=settings.CONTACT_INDUSTRY_AGENT_TEMPLATE_ID,
                sender=sender,
                spam_control=spam_control,
            )
            response.raise_for_status()

    def send_user_email(self, form):
        response = form.save(
            form_url=self.request.path,
            email_address=form.cleaned_data['email_address'],
            template_id=settings.CONTACT_INDUSTRY_USER_TEMPLATE_ID,
            email_reply_to_id=settings.CONTACT_INDUSTRY_USER_REPLY_TO_ID,
        )
        response.raise_for_status()

    def form_valid(self, form):
        self.send_agent_email(form)
        self.send_user_email(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = get_sectors_as_string(dbt_sectors)

        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
        )
