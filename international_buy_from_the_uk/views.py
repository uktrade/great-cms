from directory_forms_api_client import helpers
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from config import settings
from core.helpers import get_sender_ip_address
from international_buy_from_the_uk import forms
from international_buy_from_the_uk.core.helpers import get_url
from international_buy_from_the_uk.services import (
    get_case_study,
    get_company_profile,
    search_companies,
)
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
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Buy from the UK', 'url': '/international/buy-from-the-uk/'},
        ]
        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
            breadcrumbs=breadcrumbs,
        )


# Find a supplier


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
        results, count = search_companies(
            form.cleaned_data['q'], form.cleaned_data['industries'], form.cleaned_data['page'], self.page_size
        )
        try:
            paginator = Paginator(range(count), self.page_size)
            pagination = paginator.page(form.cleaned_data['page'])
            page_range = paginator.get_elided_page_range(form.cleaned_data['page'], on_each_side=1, on_ends=1)
        except EmptyPage:
            return self.handle_empty_page(form)
        else:
            context = self.get_context_data(
                results=results,
                pagination=pagination,
                form=form,
                page_range=page_range,
            )
            return TemplateResponse(self.request, self.template_name, context)

    @staticmethod
    def handle_empty_page(form):
        url_str = get_url(form)
        url = '{url}{url_str}&page=1'.format(
            url=reverse('international_buy_from_the_uk:find-a-supplier'), url_str=url_str
        )
        return redirect(url)

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Buy from the UK', 'url': '/international/buy-from-the-uk/'},
        ]
        return super().get_context_data(
            **kwargs,
            breadcrumbs=breadcrumbs,
        )


class CompanyProfileMixin:
    @cached_property
    def company(self):
        company = get_company_profile(self.kwargs['company_number'])
        return company


class FindASupplierProfileView(CompanyProfileMixin, GA360Mixin, TemplateView):
    template_name = 'buy_from_the_uk/find_a_supplier/profile.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-profile',
            business_unit='Buy from the UK',
            site_section='Find a supplier profile',
        )

    def get_context_data(self, **kwargs):
        find_a_supplier_url = reverse_lazy('international_buy_from_the_uk:find-a-supplier')
        if self.request.GET.get('back'):
            find_a_supplier_url = self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Buy from the UK', 'url': '/international/buy-from-the-uk/'},
            {'name': 'Find a UK supplier', 'url': find_a_supplier_url},
        ]
        return super().get_context_data(
            **kwargs,
            company=self.company,
            breadcrumbs=breadcrumbs,
        )


class CaseStudyMixin:
    @cached_property
    def case_study(self):
        case_study = get_case_study(self.kwargs['case_study_id'])
        return case_study


class FindASupplierCaseStudyView(CaseStudyMixin, GA360Mixin, TemplateView):
    template_name = 'buy_from_the_uk/find_a_supplier/case_study.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-case-study',
            business_unit='Buy from the UK',
            site_section='Find a supplier case study',
        )

    def get_context_data(self, **kwargs):
        find_a_supplier_url = reverse_lazy('international_buy_from_the_uk:find-a-supplier')
        company_profile_url = reverse_lazy(
            'international_buy_from_the_uk:find-a-supplier-profile',
            kwargs={'company_number': self.case_study['company']['number']},
        )
        if self.request.GET.get('back'):
            find_a_supplier_url = self.request.get_full_path().split('back=', 1)[1]
            company_profile_url = company_profile_url + '?back=' + self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Buy from the UK', 'url': '/international/buy-from-the-uk/'},
            {'name': 'Find a UK supplier', 'url': find_a_supplier_url},
            {
                'name': self.case_study['company']['name'],
                'url': company_profile_url,
            },
        ]
        return super().get_context_data(
            **kwargs,
            case_study=self.case_study,
            breadcrumbs=breadcrumbs,
        )


class FindASupplierContactView(CompanyProfileMixin, GA360Mixin, FormView):
    form_class = forms.FindASupplierContactForm
    template_name = 'buy_from_the_uk/find_a_supplier/contact.html'
    company_email_address = None

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-contact',
            business_unit='Buy from the UK',
            site_section='Find a supplier contact',
        )

    def get_success_url(self):
        success_url = (
            reverse_lazy('international:contact') + '?success=true' + '&next=' + '/international/buy-from-the-uk'
        )
        return success_url

    def send_email(self, form):
        sender = helpers.Sender(
            email_address=form.cleaned_data['email_address'],
            country_code=form.cleaned_data['country'],
            ip_address=get_sender_ip_address(self.request),
        )
        spam_control = helpers.SpamControl(contents=[form.cleaned_data['subject'], form.cleaned_data['body']])
        response = form.save(
            template_id=settings.CONTACT_FAS_COMPANY_NOTIFY_TEMPLATE_ID,
            email_address=self.company['email_address'],
            form_url=self.request.path,
            sender=sender,
            spam_control=spam_control,
        )
        response.raise_for_status()

    def form_valid(self, form):
        form.cleaned_data['country'] = get_location_display(form.cleaned_data['country'])
        self.send_email(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = get_sectors_as_string(dbt_sectors)

        find_a_supplier_url = reverse_lazy('international_buy_from_the_uk:find-a-supplier')

        company_profile_url = reverse_lazy(
            'international_buy_from_the_uk:find-a-supplier-profile',
            kwargs={'company_number': self.company['number']},
        )

        if self.request.GET.get('back'):
            find_a_supplier_url = self.request.get_full_path().split('back=', 1)[1]
            company_profile_url = company_profile_url + '?back=' + self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Buy from the UK', 'url': '/international/buy-from-the-uk/'},
            {'name': 'Find a UK supplier', 'url': find_a_supplier_url},
            {'name': self.company['name'], 'url': company_profile_url},
        ]
        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
            breadcrumbs=breadcrumbs,
            company=self.company,
        )
