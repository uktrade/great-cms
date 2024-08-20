import directory_components.helpers
from directory_forms_api_client import helpers
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.html import escape, mark_safe
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from config import settings
from core.helpers import get_sender_ip_address
from directory_api_client.client import api_client
from international_buy_from_the_uk import forms
from international_investment.core.helpers import get_location_display
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
        form.cleaned_data['country'] = get_location_display(form.cleaned_data['country'])
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


class CompanyParser(directory_components.helpers.CompanyParser):

    def serialize_for_template(self):
        if not self.data:
            return {}
        return {
            **self.data,
            'date_of_creation': self.date_of_creation,
            'address': self.address,
            'sectors': self.sectors_label,
            'keywords': self.keywords,
            'employees': self.employees_label,
            'expertise_industries': self.expertise_industries_label,
            'expertise_regions': self.expertise_regions_label,
            'expertise_countries': self.expertise_countries_label,
            'expertise_languages': self.expertise_languages_label,
            'has_expertise': self.has_expertise,
            'expertise_products_services': (self.expertise_products_services_label),
            'is_in_companies_house': self.is_in_companies_house,
        }


def get_results_from_search_response(response):
    parsed = response.json()
    formatted_results = []

    for result in parsed['hits']['hits']:
        parser = CompanyParser(result['_source'])
        formatted = parser.serialize_for_template()
        if 'highlight' in result:
            highlighted = '...'.join(
                result['highlight'].get('description', '') or result['highlight'].get('summary', '')
            )
            # escape all html tags other than <em> and </em>
            highlighted_escaped = escape(highlighted).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
            formatted['highlight'] = mark_safe(highlighted_escaped)
        formatted_results.append(formatted)

    parsed['results'] = formatted_results
    return parsed


class SubmitFormOnGetMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET or {}
        if data:
            kwargs['data'] = data
        return kwargs

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FindASupplierSearchView(GA360Mixin, SubmitFormOnGetMixin, FormView):
    template_name = 'buy_from_the_uk/find_a_supplier/search.html'
    form_class = forms.SearchForm
    page_size = 10

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-search',
            business_unit='Buy from the UK',
            site_section='Find a supplier search',
        )

    def form_valid(self, form):
        results, count = self.get_results_and_count(form)
        try:
            paginator = Paginator(range(count), self.page_size)
            pagination = paginator.page(form.cleaned_data['page'])
        except EmptyPage:
            return self.handle_empty_page(form)
        else:
            context = self.get_context_data(
                results=results,
                pagination=pagination,
                form=form,
                # filters=get_filters_labels(form.cleaned_data),
                # pages_after_current=paginator.num_pages - pagination.number,
                # paginator_url=helpers.get_paginator_url(form.cleaned_data)
            )
            return TemplateResponse(self.request, self.template_name, context)

    def get_results_and_count(self, form):
        response = api_client.company.search_find_a_supplier(
            term=form.cleaned_data['q'],
            page=form.cleaned_data['page'],
            sectors=form.cleaned_data['industries'],
            size=self.page_size,
            use_fallback_cache=False,
        )
        response.raise_for_status()
        formatted = get_results_from_search_response(response)
        return formatted['results'], formatted['hits']['total']['value']

    @staticmethod
    def handle_empty_page(form):
        url = '{url}?q={q}&page={page}'.format(
            url=reverse('international_buy_from_the_uk:find-a-supplier'), q=form.cleaned_data['q'], page=1
        )
        return redirect(url)


class FindASupplierProfileView(GA360Mixin, TemplateView):
    template_name = 'buy_from_the_uk/find_a_supplier/profile.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-profile',
            business_unit='Buy from the UK',
            site_section='Find a supplier profile',
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )
