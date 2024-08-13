from directory_forms_api_client import actions
from directory_forms_api_client.helpers import Sender
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from core.helpers import check_url_host_is_safelisted
from international_buy_from_the_uk import forms
from international_online_offer.core.region_sector_helpers import get_sectors_as_string
from international_online_offer.services import get_dbt_sectors


class ContactView(GA360Mixin, FormView):
    form_class = forms.ContactForm
    template_name = 'buy_from_the_uk/contact.html'
    # subject = 'Great.gov.uk International contact form'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Buy from the UK',
            site_section='contact',
        )

    def get_success_url(self):
        success_url = reverse_lazy('international:contact') + '?success=true'
        if self.request.GET.get('next'):
            success_url = success_url + '&next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def submit_feedback(self, form):
        cleaned_data = form.cleaned_data
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

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        dbt_sectors = [
            {
                'id': 1,
                'sector_id': 'SL0003',
                'full_sector_name': 'Advanced engineering : Metallurgical process plant',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': 'Metallurgical process plant',
                'sub_sub_sector_name': '',
            },
            {
                'id': 6,
                'sector_id': 'SL00056',
                'full_sector_name': 'Advanced engineering',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': '',
                'sub_sub_sector_name': '',
            },
            {
                'id': 2,
                'sector_id': 'SL0004',
                'full_sector_name': 'Advanced engineering : Metals, minerals and materials',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': 'Metals, minerals and materials',
                'sub_sub_sector_name': '',
            },
            {
                'id': 3,
                'sector_id': 'SL0050',
                'full_sector_name': 'Automotive',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': '',
                'sub_sub_sector_name': '',
            },
            {
                'id': 4,
                'sector_id': 'SL0052',
                'full_sector_name': 'Automotive : Component manufacturing : Bodies and coachwork',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': 'Component manufacturing',
                'sub_sub_sector_name': 'Bodies and coachwork',
            },
            {
                'id': 5,
                'sector_id': 'SL0053',
                'full_sector_name': 'Automotive : Component manufacturing : Electronic components',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Automotive',
                'sub_sector_name': 'Component manufacturing',
                'sub_sub_sector_name': 'Electronic components',
            },
        ]
        autocomplete_sector_data = get_sectors_as_string(dbt_sectors)

        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
        )
