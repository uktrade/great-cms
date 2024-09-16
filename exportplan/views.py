import json
from datetime import datetime

import sentry_sdk
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.views.generic import FormView, TemplateView, View
from great_components.mixins import GA360Mixin
from requests.exceptions import RequestException

from core.forms import HCSATForm
from core.mixins import HCSATMixin, PageTitleMixin
from core.utils import choices_to_key_value
from directory_api_client.client import api_client
from directory_constants import choices
from exportplan import forms
from exportplan.context import (
    CountryDataContextProvider,
    FactbookDataContextProvider,
    PDFContextProvider,
)
from exportplan.core import data, helpers, parsers, serializers
from exportplan.core.processor import ExportPlanProcessor
from exportplan.utils import render_to_pdf


class ExportPlanMixin:
    def dispatch(self, request, *args, **kwargs):
        serializer = serializers.ExportPlanSerializer(data={'ui_progress': {self.slug: {'modified': datetime.now()}}})
        serializer.is_valid()
        helpers.update_exportplan(
            id=self.processor.data['pk'],
            sso_session_id=self.request.user.session_id,
            data=serializer.data,
        )
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def processor(self):
        export_plan_id = int(self.kwargs['id'])
        export_plan = helpers.get_exportplan(self.request.user.session_id, export_plan_id)
        return ExportPlanProcessor(export_plan)

    @cached_property
    def export_plan(self):
        return parsers.ExportPlanParser(self.processor.data)

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None
        return data.SECTIONS[data.SECTION_SLUGS[data.SECTION_SLUGS.index(self.slug) + 1]]

    @property
    def current_section(self):
        return self.processor.build_current_url(self.slug)

    def get_context_data(self, **kwargs):
        industries = [name for _, name in choices.INDUSTRIES]
        country_choices = choices_to_key_value(choices.COUNTRY_CHOICES)
        return super().get_context_data(
            next_section=self.next_section,
            current_section=self.current_section,
            export_plan_progress=self.processor.calculate_ep_progress(),
            sections=self.processor.build_export_plan_sections(),
            export_plan=self.processor.data,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            export_plan_landing_page_url=self.processor.landing_page_url(),
            **kwargs,
        )


class LessonDetailsMixin:
    @property
    def lesson_details(self):
        lessons = self.current_section['lessons']
        return helpers.get_lesson_details(lessons)

    def get_context_data(self, **kwargs):
        return super().get_context_data(lesson_details=self.lesson_details, **kwargs)


class FormContextMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        form_field_values = self.get_form().fields.values()

        field_names = list(self.form_class.base_fields.keys())

        field_labels = [field.label for field in form_field_values]

        field_placeholders = [field.widget.attrs.get('placeholder', '') for field in form_field_values]

        field_tooltip = [field.widget.attrs.get('tooltip', '') for field in form_field_values]

        field_example = [field.widget.attrs.get('example', '') for field in form_field_values]

        field_description = [field.widget.attrs.get('description', '') for field in form_field_values]

        field_currency = [field.widget.attrs.get('currency', '') for field in form_field_values]

        field_choices = [
            [{'value': key, 'label': label} for key, label in field.choices] if hasattr(field, 'choices') else ''
            for field in form_field_values
        ]

        field_types = [type(field.widget).__name__ for field in form_field_values]

        form_fields = [
            {
                'name': name,
                'label': label,
                'field_type': field_type,
                'placeholder': placeholder,
                'tooltip': tooltip,
                'example': example,
                'description': description,
                'currency': currency,
                'choices': choices,
            }
            for name, label, field_type, placeholder, tooltip, example, description, currency, choices in zip(
                field_names,
                field_labels,
                field_types,
                field_placeholders,
                field_tooltip,
                field_example,
                field_description,
                field_currency,
                field_choices,
            )
        ]
        context['form_initial'] = json.dumps(context['form'].initial)
        context['form_fields'] = json.dumps(form_fields)
        return context


class ExportPlanSectionView(GA360Mixin, ExportPlanMixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']


class ExportPlanMarketingApproachView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    slug = 'marketing-approach'
    title = 'Marketing approach'
    text = ''
    image = '/static/images/marketing-approach-header.png'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_choices = choices_to_key_value(choices.MARKET_ROUTE_CHOICES)
        promotional_choices = choices_to_key_value(choices.PRODUCT_PROMOTIONAL_CHOICES)
        target_age_group_choices = choices_to_key_value(choices.TARGET_AGE_GROUP_CHOICES)
        context['route_to_markets'] = self.export_plan.data['route_to_markets']
        context['route_choices'] = route_choices
        context['target_age_group_choices'] = target_age_group_choices
        context['promotional_choices'] = promotional_choices
        context['selected_age_groups'] = self.processor.data['ui_options'].get(self.slug, {}).get('target_ages', [])
        context['marketing_approach'] = self.processor.data['marketing_approach']
        return context


class ExportPlanAdaptingYourProductView(
    PageTitleMixin, LessonDetailsMixin, FormContextMixin, ExportPlanSectionView, FormView
):
    form_class = forms.ExportPlanAdaptingYourProductForm
    success_url = reverse_lazy('exportplan:adapting-your-product')
    title = 'Adapting your product'
    text = ''
    image = '/static/images/adapting-your-product-header.png'

    def get_initial(self):
        return self.processor.data['adaptation_target_market']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['target_market_documents'] = self.processor.data['target_market_documents']
        return context


class ExportPlanTargetMarketsResearchView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    slug = 'target-markets-research'
    title = 'Target market research'
    image = '/static/images/marketing-approach-header.png'
    text = ''

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        target_age_group_choices = choices_to_key_value(choices.TARGET_AGE_GROUP_CHOICES)
        context['target_age_group_choices'] = target_age_group_choices

        context['selected_age_groups'] = self.processor.data['ui_options'].get(self.slug, {}).get('target_ages', [])
        context['target_markets_research'] = self.processor.data['target_markets_research']

        return context


class ExportPlanBusinessObjectivesView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Business objectives'
    text = ''
    image = '/static/images/business-objectives-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['company_objectives'] = self.processor.data['company_objectives']
        context['objectives'] = self.processor.data['objectives']
        return context


class ExportPlanAboutYourBusinessView(PageTitleMixin, ExportPlanSectionView):
    title = 'About your business'
    text = ''
    image = '/static/images/about-your-business-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['turnover_choices'] = choices_to_key_value(choices.TURNOVER_CHOICES)
        context['about_your_business_data'] = self.processor.data['about_your_business']
        return context


class CostsAndPricingView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    success_url = reverse_lazy('exportplan:about-your-business')
    title = 'Costs And Pricing'
    text = ''
    image = '/static/images/costs-and-pricing-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['export_unit_choices'] = choices_to_key_value(choices.EXPORT_UNITS)
        currency_choices = (('eur', 'EUR'), ('gbp', 'GBP'), ('usd', 'USD'))
        context['currency_choices'] = choices_to_key_value(currency_choices)
        context['costs_and_pricing_data'] = serializers.ExportPlanSerializer().cost_and_pricing_to_json(
            self.processor.data
        )
        context['calculated_pricing'] = self.processor.calculated_cost_pricing()
        return context


class GettingPaidView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Getting paid'
    text = ''
    image = '/static/images/getting-paid-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['payment_method_choices'] = choices_to_key_value(choices.PAYMENT_METHOD_OPTIONS)
        context['payment_term_choices'] = choices_to_key_value(choices.PAYMENT_TERM_OPTIONS)
        transport_choices = {
            'All forms of transport': choices_to_key_value(choices.TRANSPORT_OPTIONS),
            'Water transport': choices_to_key_value(choices.WATER_TRANSPORT_OPTIONS),
        }
        context['transport_choices'] = transport_choices

        context['getting_paid_data'] = self.processor.data['getting_paid']
        return context


class FundingAndCreditView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Funding and credit'
    text = ''
    image = '/static/images/funding-and-credit-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['funding_options'] = choices_to_key_value(choices.FUNDING_OPTIONS)
        context['funding_and_credit'] = self.processor.data['funding_and_credit']

        calculated_pricing = self.processor.calculated_cost_pricing()
        context['estimated_costs_per_unit'] = calculated_pricing['calculated_cost_pricing'].get(
            'estimated_costs_per_unit', ''
        )
        context['funding_credit_options'] = self.processor.data.get('funding_credit_options', [])
        return context


class TravelBusinessPoliciesView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Travel plan'
    text = ''
    image = '/static/images/travel-plan-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['travel_business_policies'] = self.processor.data['travel_business_policies']
        context['business_trips'] = self.processor.data['business_trips']
        context['travel_advice_covid19'] = settings.TRAVEL_ADVICE_COVID19
        context['travel_advice_foreign'] = settings.TRAVEL_ADVICE_FOREIGN
        return context


class BusinessRiskView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Business Risk'
    text = ''
    image = '/static/images/business-risk-header.png'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['risk_likelihood_options'] = choices_to_key_value(choices.RISK_LIKELIHOOD_OPTIONS)
        context['risk_impact_options'] = choices_to_key_value(choices.RISK_IMPACT_OPTIONS)
        context['business_risks'] = self.processor.data['business_risks']
        return context


class BaseFormView(GA360Mixin, FormView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    success_url = reverse_lazy('exportplan:index')

    def get_initial(self):
        return self.request.user.company.serialize_for_form()

    def form_valid(self, form):
        try:
            response = api_client.company.profile_update(
                sso_session_id=self.request.user.session_id, data=self.serialize_form(form)
            )
            response.raise_for_status()
        except RequestException:
            self.send_update_error_to_sentry(user=self.request.user, api_response=response)
            raise
        return redirect(self.success_url)

    def serialize_form(self, form):
        return form.cleaned_data

    @staticmethod
    def send_update_error_to_sentry(user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending
        sentry_sdk.set_user({'hashed_uuid': user.hashed_uuid, 'user_email': user.email})
        sentry_sdk.set_extra('api_response', str(api_response.content))
        sentry_sdk.capture_message('Updating company profile failed')


class LogoFormView(PageTitleMixin, BaseFormView):
    def get_initial(self):
        return {}

    form_class = forms.LogoForm
    template_name = 'exportplan/logo-form.html'
    success_message = 'Logo updated'
    title = 'Upload your logo'


class ExportPlanServicePage(GA360Mixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    template_name = 'exportplan/service_page.html'


class PDFDownload(
    View,
    PDFContextProvider,
    CountryDataContextProvider,
    FactbookDataContextProvider,
):
    def get(self, request, *args, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        context['risk_impact_options'] = choices_to_key_value(choices.RISK_IMPACT_OPTIONS)
        context['risk_likelihood_options'] = choices_to_key_value(choices.RISK_LIKELIHOOD_OPTIONS)
        context['content_icons'] = False
        pdf_reponse, pdf_file = render_to_pdf('exportplan/pdf_download.html', context)

        helpers.upload_exportplan_pdf(
            sso_session_id=request.user.session_id, exportplan_id=int(self.kwargs['id']), file=pdf_file
        )
        response = HttpResponse(pdf_reponse, content_type='application/pdf')
        filename = f'{slugify(context.get("export_plan").data.get("name","export_plan"))}.pdf'
        response['Content-Disposition'] = f'inline; filename={filename}'
        return response


class ExportPlanIndex(GA360Mixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    template_name = 'exportplan/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['exportplan_list'] = helpers.get_exportplan_detail_list(self.request.user.session_id)
        return context


class ExportPlanStart(GA360Mixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    template_name = 'exportplan/start.html'


class ExportPlanUpdate(GA360Mixin, TemplateView):
    # This page is used to allow users to set a product/market in an export plan that doesn't have both
    export_plan = None

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    template_name = 'exportplan/start.html'

    def dispatch(self, request, *args, **kwargs):
        id = int(self.kwargs['id'])
        self.export_plan = helpers.get_exportplan(self.request.user.session_id, id)
        processor = ExportPlanProcessor(self.export_plan)
        if processor.has_product_and_market():
            return redirect(reverse_lazy('exportplan:dashboard', kwargs={'id': id}))
        return super(ExportPlanUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_plan'] = self.export_plan
        return context


class ExportPlanDashBoard(
    GA360Mixin,
    HCSATMixin,
    TemplateView,
    FormView,
):
    export_plan = None

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    template_name = 'exportplan/dashboard_page.html'
    form_class = HCSATForm
    hcsat_service_name = 'export_plan'

    def dispatch(self, request, *args, **kwargs):
        id = int(self.kwargs['id'])
        self.export_plan = helpers.get_exportplan(self.request.user.session_id, id)
        processor = ExportPlanProcessor(self.export_plan)
        if not processor.has_product_and_market():
            return redirect(reverse_lazy('exportplan:update', kwargs={'id': id}))
        return super(ExportPlanDashBoard, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        processor = ExportPlanProcessor(self.export_plan)
        context['sections'] = processor.build_export_plan_sections()
        context['export_plan_progress'] = processor.calculate_ep_progress()
        context['export_plan'] = self.export_plan
        context['export_plan_download_link'] = reverse_lazy(
            'exportplan:pdf-download', kwargs={'id': self.export_plan.get('pk')}
        )
        context = self.set_csat_and_stage(self.request, context, self.hcsat_service_name, self.form_class)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        return context

    def get_success_url(self):
        id = self.kwargs['id']
        return reverse_lazy('exportplan:dashboard', kwargs={'id': id})

    def post(self, request, *args, **kwargs):
        form_class = self.form_class

        hcsat = self.get_hcsat(request, self.hcsat_service_name)
        post_data = self.request.POST

        if 'cancelButton' in post_data:
            """
            Redirect user if 'cancelButton' is found in the POST data
            """
            if hcsat:
                hcsat.stage = 2
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

    def form_invalid(self, form):
        super().form_invalid(form)
        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse(form.errors, status=400)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        super().form_valid(form)
        id = self.kwargs['id']

        hcsat = form.save(commit=False)

        # js version handles form progression in js file, so keep on 0 for reloads
        if 'js_enabled' in self.request.get_full_path():
            hcsat.stage = 0

        # if in second part of form (satisfaction=None) or not given in first part, persist existing satisfaction rating
        hcsat = self.persist_existing_satisfaction(self.request, self.hcsat_service_name, hcsat)

        # Apply data specific to this service
        hcsat.URL = reverse_lazy('exportplan:dashboard', kwargs={'id': id})
        hcsat.user_journey = 'EXPORT_PLAN_UPDATE'
        hcsat.session_key = self.request.session.session_key

        hcsat.save()

        self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse({'pk': hcsat.pk})
        return HttpResponseRedirect(self.get_success_url())
