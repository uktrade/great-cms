from directory_forms_api_client import helpers
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin  # /PS-IGNORE
from wagtailcache.cache import nocache_page

from config import settings
from core.constants import HCSatStage, TemplateTagsEnum
from core.forms import HCSATForm
from core.helpers import get_sender_ip_address, get_template_id, international_url
from core.mixins import HCSATMixin
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


@method_decorator(nocache_page, name='get')
class ContactView(GA360Mixin, HCSATMixin, FormView):  # /PS-IGNORE
    form_class = forms.ContactForm
    template_name = 'buy_from_the_uk/contact.html'
    hcsat_form = HCSATForm
    hcsat_service_name = 'buy_from_the_uk'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Buy from the UK',
            site_section='contact',
        )

    def get_success_url(self):
        success_url = reverse('international_buy_from_the_uk:contact') + '?success=true'
        return success_url

    def post(self, request, *args, **kwargs):
        if 'email_address' in request.POST:
            # contact form
            return super().post(request)
        else:
            # hcsat form
            form_class = self.hcsat_form
            hcsat = self.get_hcsat(request, self.hcsat_service_name)
            post_data = request.POST
            if 'cancelButton' in post_data:
                """
                Redirect user if 'cancelButton' is found in the POST data
                """
                if hcsat:
                    hcsat.stage = HCSatStage.COMPLETED.value
                    hcsat.save()
                return HttpResponseRedirect(self.get_success_url())

            form = form_class(post_data)

            if form.is_valid():
                if hcsat:
                    form = form_class(post_data, instance=hcsat)
                    form.is_valid()
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

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
        if type(form) is HCSATForm:
            js_enabled = False
            hcsat = form.save(commit=False)

            # js version handles form progression in js file, so keep on 0 for reloads
            if 'js_enabled' in self.request.get_full_path():
                hcsat.stage = HCSatStage.NOT_STARTED.value
                js_enabled = True

            # if in second part of form (satisfaction=None) or not given in first part, persist existing satisfaction rating  # noqa: E501
            hcsat = self.persist_existing_satisfaction(self.request, self.hcsat_service_name, hcsat)

            # Apply data specific to this service
            hcsat.URL = f'/{international_url(self.request)}/buy-from-the-uk/contact'
            hcsat.user_journey = 'BUY_FROM_THE_UK_CONTACT'
            hcsat.session_key = self.request.session.session_key
            hcsat.service_name = 'buy_from_the_uk'

            hcsat.save(js_enabled=js_enabled)

            self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

            if 'js_enabled' in self.request.get_full_path():
                return JsonResponse({'pk': hcsat.pk})
            return HttpResponseRedirect(self.get_success_url())
        else:
            form.cleaned_data['country'] = get_location_display(form.cleaned_data['country'])
            self.send_agent_email(form)
            self.send_user_email(form)
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = get_sectors_as_string(dbt_sectors)
        buy_from_the_uk_url = f'/{international_url(self.request)}/buy-from-the-uk/'
        breadcrumbs = [
            {'name': 'Home', 'url': f'/{international_url(self.request)}/'},
            {'name': 'Buy from the UK', 'url': buy_from_the_uk_url},
        ]

        context = super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
            breadcrumbs=breadcrumbs,
            continue_url=buy_from_the_uk_url,
        )

        context = self.set_csat_and_stage(self.request, context, self.hcsat_service_name, form=self.hcsat_form)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        return context

    def form_invalid(self, form):
        super().form_invalid(form)
        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse(form.errors, status=400)
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


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


class FindASupplierSearchView(GA360Mixin, SubmitFormOnGetMixin, FormView):  # /PS-IGNORE
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
        page_num = form.cleaned_data['page']
        results, count = search_companies(
            form.cleaned_data['q'], form.cleaned_data['industries'], page_num, self.page_size
        )

        paginator = Paginator(range(count), self.page_size)

        # Bespoke logic to handle redirection
        try:
            paginator.page(page_num)
        except EmptyPage:
            return self.handle_empty_page(form)

        page_obj = paginator.get_page(page_num)
        elided_page_range = [
            page_num
            for page_num in page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
        ]

        context = self.get_context_data(
            results=results,
            page_obj=page_obj,
            elided_page_range=elided_page_range,
            form=form,
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
            {'name': 'Home', 'url': f'/{international_url(self.request)}/'},
            {'name': 'Buy from the UK', 'url': f'/{international_url(self.request)}/buy-from-the-uk/'},
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


class FindASupplierProfileView(CompanyProfileMixin, GA360Mixin, TemplateView):  # /PS-IGNORE
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
            {'name': 'Home', 'url': f'/{international_url(self.request)}/'},
            {'name': 'Buy from the UK', 'url': f'/{international_url(self.request)}/buy-from-the-uk/'},
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


class FindASupplierCaseStudyView(CaseStudyMixin, GA360Mixin, TemplateView):  # /PS-IGNORE
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
            {'name': 'Home', 'url': f'/{international_url(self.request)}/'},
            {'name': 'Buy from the UK', 'url': f'/{international_url(self.request)}/buy-from-the-uk/'},
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


@method_decorator(nocache_page, name='get')
class FindASupplierContactView(CompanyProfileMixin, GA360Mixin, HCSATMixin, FormView):  # /PS-IGNORE
    form_class = forms.FindASupplierContactForm
    template_name = 'buy_from_the_uk/find_a_supplier/contact.html'
    hcsat_form = HCSATForm
    company_email_address = None
    hcsat_service_name = 'find_a_supplier'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-supplier-contact',
            business_unit='Buy from the UK',
            site_section='Find a supplier contact',
        )

    def get_success_url(self):
        success_url = (
            reverse(
                'international_buy_from_the_uk:find-a-supplier-contact',
                kwargs={'company_number': self.kwargs['company_number']},
            )
            + '?success=true'
        )
        return success_url

    def post(self, request, *args, **kwargs):
        if 'email_address' in request.POST:
            # contact form
            return super().post(request)
        else:
            # hcsat form
            form_class = self.hcsat_form
            hcsat = self.get_hcsat(request, self.hcsat_service_name)
            post_data = request.POST
            if 'cancelButton' in post_data:
                """
                Redirect user if 'cancelButton' is found in the POST data
                """
                if hcsat:
                    hcsat.stage = HCSatStage.COMPLETED.value
                    hcsat.save()
                return HttpResponseRedirect(self.get_success_url())

            form = form_class(post_data)

            if form.is_valid():
                if hcsat:
                    form = form_class(post_data, instance=hcsat)
                    form.is_valid()
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def send_email(self, form):
        sender = helpers.Sender(
            email_address=form.cleaned_data['email_address'],
            country_code=form.cleaned_data['country'],
            ip_address=get_sender_ip_address(self.request),
        )
        spam_control = helpers.SpamControl(contents=[form.cleaned_data['subject'], form.cleaned_data['body']])
        response = form.save(
            template_id=get_template_id(TemplateTagsEnum.CONTACT_FIND_SUPPLIER_OR_SPECIALIST_COMPANY),
            email_address=self.company['email_address'],
            form_url=self.request.path,
            sender=sender,
            spam_control=spam_control,
        )
        response.raise_for_status()

    def form_valid(self, form):
        if type(form) is HCSATForm:
            js_enabled = False
            hcsat = form.save(commit=False)

            # js version handles form progression in js file, so keep on 0 for reloads
            if 'js_enabled' in self.request.get_full_path():
                hcsat.stage = HCSatStage.NOT_STARTED.value
                js_enabled = True

            # if in second part of form (satisfaction=None) or not given in first part, persist existing satisfaction rating  # noqa: E501
            hcsat = self.persist_existing_satisfaction(self.request, self.hcsat_service_name, hcsat)

            # Apply data specific to this service
            hcsat.URL = f'/{international_url(self.request)}/buy-from-the-uk/find-a-supplier'
            hcsat.user_journey = 'FIND_A_SUPPLIER_CONTACT'
            hcsat.session_key = self.request.session.session_key
            hcsat.service_name = 'find_a_supplier'

            hcsat.save(js_enabled=js_enabled)

            self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

            if 'js_enabled' in self.request.get_full_path():
                return JsonResponse({'pk': hcsat.pk})
            return HttpResponseRedirect(self.get_success_url())
        else:
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
            {'name': 'Home', 'url': f'/{international_url(self.request)}/'},
            {'name': 'Buy from the UK', 'url': f'/{international_url(self.request)}/buy-from-the-uk/'},
            {'name': 'Find a UK supplier', 'url': find_a_supplier_url},
            {'name': self.company['name'], 'url': company_profile_url},
        ]

        context = super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
            breadcrumbs=breadcrumbs,
            continue_url=company_profile_url,
            company=self.company,
            public_key=settings.RECAPTCHA_PUBLIC_KEY,
            recaptcha_domain=settings.RECAPTCHA_DOMAIN,
        )

        context = self.set_csat_and_stage(self.request, context, self.hcsat_service_name, form=self.hcsat_form)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        return context

    def form_invalid(self, form):
        super().form_invalid(form)
        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse(form.errors, status=400)
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
