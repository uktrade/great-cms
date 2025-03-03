from directory_forms_api_client import helpers
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin  # /PS-IGNORE

from config import settings
from core.constants import HCSatStage
from core.forms import HCSATForm
from core.helpers import get_sender_ip_address
from core.mixins import HCSATMixin
from international_buy_from_the_uk.services import get_case_study, get_company_profile
from international_investment.core.helpers import get_location_display
from international_investment_support_directory import forms
from international_investment_support_directory.core.helpers import get_url
from international_investment_support_directory.services import search_companies
from international_online_offer.core.region_sector_helpers import get_sectors_as_string
from international_online_offer.services import get_dbt_sectors


class SubmitFormOnGetMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET or {}
        if data:
            kwargs['data'] = data
        return kwargs

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FindASpecialistSearchView(GA360Mixin, SubmitFormOnGetMixin, FormView):  # /PS-IGNORE
    template_name = 'investment_support_directory/find_a_specialist/search.html'
    form_class = forms.SearchForm
    page_size = 10

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-specialist-search',
            business_unit='Investment Support Directory',
            site_section='Find a specialist search',
        )

    def form_valid(self, form):
        page_num = form.cleaned_data['page']
        results, count = search_companies(
            query=form.cleaned_data['q'],
            expertise_industries=form.cleaned_data.get('expertise_industries'),
            expertise_regions=form.cleaned_data.get('expertise_regions'),
            expertise_countries=form.cleaned_data.get('expertise_countries'),
            expertise_languages=form.cleaned_data.get('expertise_languages'),
            expertise_financial=form.cleaned_data.get('expertise_financial'),
            expertise_products_services_labels=form.cleaned_data.get('expertise_products_services_labels'),
            page=page_num,
            page_size=self.page_size,
        )

        paginator = Paginator(range(count), self.page_size)

        # Bespoke logic to handle redirection
        try:
            paginator.page(page_num)
        except EmptyPage:
            return self.handle_empty_page(form)

        page_obj = paginator.get_page(page_num)
        elided_page_range = page_obj.get_elided_page_range(page_num, on_each_side=1, on_ends=1)

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
            url=reverse('international_investment_support_directory:find-a-specialist'), url_str=url_str
        )
        return redirect(url)

    def get_context_data(self, **kwargs):
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Investment support directory', 'url': '/international/investment-support-directory/'},
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


class FindASpecialistProfileView(CompanyProfileMixin, GA360Mixin, TemplateView):  # /PS-IGNORE
    template_name = 'investment_support_directory/find_a_specialist/profile.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-specialist-profile',
            business_unit='Investment Support Directory',
            site_section='Find a specialist profile',
        )

    def get_context_data(self, **kwargs):
        find_a_specialist_url = reverse_lazy('international_investment_support_directory:find-a-specialist')
        if self.request.GET.get('back'):
            find_a_specialist_url = self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Investment support directory', 'url': '/international/investment-support-directory/'},
            {'name': 'Find a UK specialist', 'url': find_a_specialist_url},
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


class FindASpecialistCaseStudyView(CaseStudyMixin, GA360Mixin, TemplateView):  # /PS-IGNORE
    template_name = 'investment_support_directory/find_a_specialist/case_study.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-specialist-case-study',
            business_unit='Investment support directory',
            site_section='Find a specialist case study',
        )

    def get_context_data(self, **kwargs):
        find_a_specialist_url = reverse_lazy('international_investment_support_directory:find-a-specialist')
        company_profile_url = reverse_lazy(
            'international_investment_support_directory:specialist-profile',
            kwargs={'company_number': self.case_study['company']['number']},
        )
        if self.request.GET.get('back'):
            find_a_specialist_url = self.request.get_full_path().split('back=', 1)[1]
            company_profile_url = company_profile_url + '?back=' + self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Investment support directory', 'url': '/international/investment-support-directory/'},
            {'name': 'Find a UK specialist', 'url': find_a_specialist_url},
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


class FindASpecialistContactView(CompanyProfileMixin, GA360Mixin, HCSATMixin, FormView):  # /PS-IGNORE
    form_class = forms.FindASpecialistContactForm
    hcsat_form = HCSATForm
    template_name = 'investment_support_directory/find_a_specialist/contact.html'
    company_email_address = None
    hcsat_service_name = 'isd'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='find-a-specialist-contact',
            business_unit='Investment Support Directory',
            site_section='Find a specialist contact',
        )

    def get_success_url(self):
        success_url = (
            reverse(
                'international_investment_support_directory:specialist-contact',
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
                return HttpResponseRedirect(self.get_success_url(request))

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
            template_id=settings.CONTACT_FAS_COMPANY_NOTIFY_TEMPLATE_ID,
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
            hcsat.URL = '/international/investment-support-directory'
            hcsat.user_journey = 'ISD_CONTACT'
            hcsat.session_key = self.request.session.session_key
            hcsat.service_name = 'isd'

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

        find_a_specialist_url = reverse_lazy('international_investment_support_directory:find-a-specialist')
        company_profile_url = reverse_lazy(
            'international_investment_support_directory:specialist-profile',
            kwargs={'company_number': self.company['number']},
        )
        if self.request.GET.get('back'):
            find_a_specialist_url = self.request.get_full_path().split('back=', 1)[1]
            company_profile_url = company_profile_url + '?back=' + self.request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Investment support directory', 'url': '/international/investment-support-directory/'},
            {'name': 'Find a UK specialist', 'url': find_a_specialist_url},
            {'name': self.company['name'], 'url': company_profile_url},
        ]
        context = super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
            breadcrumbs=breadcrumbs,
            company=self.company,
            continue_url='/international/investment-support-directory/',
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
