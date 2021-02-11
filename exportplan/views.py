import json
from datetime import datetime

import sentry_sdk
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from great_components.mixins import GA360Mixin
from requests.exceptions import RequestException

from core.helpers import get_comtrade_data
from core.mixins import PageTitleMixin
from core.utils import choices_to_key_value
from directory_api_client.client import api_client
from directory_constants import choices
from exportplan import data, forms, helpers, serializers


class ExportPlanMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.slug not in data.SECTIONS:
            raise Http404()
        elif data.SECTIONS[self.slug]['disabled']:
            return redirect('exportplan:service-page')

        serializer = serializers.ExportPlanSerializer(data={'ui_progress': {self.slug: {'modified': datetime.now()}}})
        serializer.is_valid()
        helpers.update_exportplan(
            id=self.request.user.export_plan.data['pk'],
            sso_session_id=self.request.user.session_id,
            data=serializer.data,
        )
        return super().dispatch(request, *args, **kwargs)

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None
        return data.SECTIONS[data.SECTION_SLUGS[data.SECTION_SLUGS.index(self.slug) + 1]]

    @property
    def current_section(self):
        return self.request.user.export_plan.build_current_url(self.slug)

    def get_context_data(self, **kwargs):
        industries = [name for _, name in choices.INDUSTRIES]
        country_choices = choices_to_key_value(choices.COUNTRY_CHOICES)
        return super().get_context_data(
            next_section=self.next_section,
            current_section=self.current_section,
            export_plan_progress=self.request.user.export_plan.calculate_ep_progress(),
            sections=self.request.user.export_plan.build_export_plan_sections(),
            export_plan=self.request.user.export_plan.data,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_choices = choices_to_key_value(choices.MARKET_ROUTE_CHOICES)
        promotional_choices = choices_to_key_value(choices.PRODUCT_PROMOTIONAL_CHOICES)
        target_age_group_choices = choices_to_key_value(choices.TARGET_AGE_GROUP_CHOICES)
        context['route_to_markets'] = self.request.user.export_plan.data['route_to_markets']
        context['route_choices'] = route_choices
        context['target_age_group_choices'] = target_age_group_choices
        context['promotional_choices'] = promotional_choices
        context['demographic_data'] = helpers.get_global_demographic_data(
            self.request.user.export_plan.data['export_countries'][0]['country_name']
        )
        context['selected_age_groups'] = (
            self.request.user.export_plan.data['ui_options'].get(self.slug, {}).get('target_ages', [])
        )
        context['marketing_approach'] = self.request.user.export_plan.data['marketing_approach']

        return context


class ExportPlanAdaptationForTargetMarketView(PageTitleMixin, FormContextMixin, ExportPlanSectionView, FormView):

    form_class = forms.ExportPlanAdaptationForTargetMarketForm
    success_url = reverse_lazy('exportplan:adaptation-for-your-target-market')
    title = 'Adaptation for your target market'

    def get_initial(self):
        return self.request.user.export_plan.data['adaptation_target_market']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['check_duties_link'] = helpers.get_check_duties_link(self.request.user.export_plan.data)
        # To do pass lanaguage from export_plan object rather then  hardcoded
        context['language_data'] = helpers.get_cia_world_factbook_data(
            country=self.request.user.export_plan.export_country_name, key='people,languages'
        )
        context['target_market_documents'] = self.request.user.export_plan.data['target_market_documents']

        return context


class ExportPlanTargetMarketsResearchView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    slug = 'target-markets-research'
    title = 'Target market research'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        target_age_group_choices = choices_to_key_value(choices.TARGET_AGE_GROUP_CHOICES)
        context['target_age_group_choices'] = target_age_group_choices
        if self.request.user.export_plan.export_country_name and self.request.user.export_plan.export_commodity_code:
            insight_data = get_comtrade_data(
                countries_list=[self.request.user.export_plan.export_country_name],
                commodity_code=self.request.user.export_plan.export_commodity_code,
            )

            context['insight_data'] = insight_data
            context['selected_age_groups'] = (
                self.request.user.export_plan.data['ui_options'].get(self.slug, {}).get('target_ages', [])
            )
        context['target_markets_research'] = self.request.user.export_plan.data['target_markets_research']
        return context


class ExportPlanBusinessObjectivesView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Business objectives'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['company_objectives'] = self.request.user.export_plan.data['company_objectives']
        context['objectives'] = self.request.user.export_plan.data['objectives']
        return context


class ExportPlanAboutYourBusinessView(PageTitleMixin, ExportPlanSectionView):

    form_class = forms.ExportPlanAboutYourBusinessForm
    success_url = reverse_lazy('exportplan:about-your-business')
    title = 'About your business'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['turnover_choices'] = choices_to_key_value(choices.TURNOVER_CHOICES)
        context['about_your_business_data'] = self.request.user.export_plan.data['about_your_business']
        return context


class CostsAndPricingView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    success_url = reverse_lazy('exportplan:about-your-business')
    title = 'Costs And Pricing'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['check_duties_link'] = helpers.get_check_duties_link(self.request.user.export_plan.data)
        context['export_unit_choices'] = choices_to_key_value(choices.EXPORT_UNITS)
        context['export_timeframe_choices'] = choices_to_key_value(choices.EXPORT_TIMEFRAME)
        currency_choices = (('eur', 'EUR'), ('gbp', 'GBP'), ('usd', 'USD'))
        context['currency_choices'] = choices_to_key_value(currency_choices)
        context['costs_and_pricing_data'] = serializers.ExportPlanSerializer().cost_and_pricing_to_json(
            self.request.user.export_plan.data
        )
        context['calculated_pricing'] = self.request.user.export_plan.calculated_cost_pricing()
        return context


class GettingPaidView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Getting paid'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['payment_method_choices'] = choices_to_key_value(choices.PAYMENT_METHOD_OPTIONS)
        context['payment_term_choices'] = choices_to_key_value(choices.PAYMENT_TERM_OPTIONS)
        transport_choices = {
            'All forms of transport': choices_to_key_value(choices.TRANSPORT_OPTIONS),
            'Water transport': choices_to_key_value(choices.WATER_TRANSPORT_OPTIONS),
        }
        context['transport_choices'] = transport_choices

        context['getting_paid_data'] = self.request.user.export_plan.data['getting_paid']

        return context


class FundingAndCreditView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = 'Funding And Credit'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['funding_options'] = choices_to_key_value(choices.FUNDING_OPTIONS)
        context['funding_and_credit'] = self.request.user.export_plan.data['funding_and_credit']

        calculated_pricing = self.request.user.export_plan.calculated_cost_pricing()
        context['estimated_costs_per_unit'] = calculated_pricing['calculated_cost_pricing'].get(
            'estimated_costs_per_unit', ''
        )
        context['funding_credit_options'] = self.request.user.export_plan.data.get('funding_credit_options', [])

        return context


class TravelBusinessPoliciesView(PageTitleMixin, LessonDetailsMixin, ExportPlanSectionView):
    title = '`Travel And Business Policies'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['travel_business_policies'] = self.request.user.export_plan.data['travel_business_policies']
        context['business_trips'] = self.request.user.export_plan.data['business_trips']
        return context


class BaseFormView(GA360Mixin, FormView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='export-plan',
        )

    success_url = '/export-plan/dashboard/'

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

    def get_context_data(self, **kwargs):
        return super().get_context_data(sections=data.SECTION_URLS, **kwargs)
