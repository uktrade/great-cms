import abc
import json

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.text import slugify

from core import helpers as core_helpers
from exportplan.core import data, helpers, parsers
from exportplan.core.processor import ExportPlanProcessor


class AbstractContextProvider(abc.ABC):
    @abc.abstractmethod
    def get_context_provider_data(self, request, **kwargs):
        return {**kwargs}


class BaseContextProvider(AbstractContextProvider):
    def __init__(self):
        self.exportplan_id = 0
        self.session_id = 0

    def get_context_provider_data(self, request, **kwargs):
        self.exportplan_id = kwargs['id']
        self.session_id = request.user.session_id
        return {}

    @cached_property
    def export_plan(self):
        user_exportplan = helpers.get_exportplan(self.session_id, self.exportplan_id)
        return parsers.ExportPlanParser(user_exportplan)


class CountryDataContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        comtrade_data = {}
        country_data = {}
        age_group_population_data = {}
        context = super().get_context_provider_data(request, **kwargs)

        if self.export_plan.export_country_code and self.export_plan.export_commodity_code:
            comtrade_data = core_helpers.get_comtrade_data(
                countries_list=[self.export_plan.export_country_code],
                commodity_code=self.export_plan.export_commodity_code,
            )

        if self.export_plan.export_country_code:
            fields_list = [
                {'model': 'GDPPerCapita', 'latest_only': True},
                {'model': 'ConsumerPriceIndex', 'latest_only': True},
                {'model': 'Income', 'latest_only': True},
                'CorruptionPerceptionsIndex',
                {'model': 'EaseOfDoingBusiness', 'latest_only': True},
                {'model': 'InternetUsage', 'latest_only': True},
                {'model': 'PopulationUrbanRural', 'filter': {'year': 2020}},
                {'model': 'PopulationData', 'filter': {'year': 2020}},
            ]
            country_data = core_helpers.get_country_data(
                countries=[self.export_plan.export_country_code],
                fields=json.dumps(fields_list),
            )

            country_data = country_data.get(self.export_plan.export_country_code)

            sections = [slugify(data.TARGET_MARKETS_RESEARCH), slugify(data.MARKETING_APPROACH)]

            # Get Urban percentages and total population
            population_dataset = country_data.get('PopulationData', {})
            urban_rural_dataset = country_data.get('PopulationUrbanRural', {})
            country_data['total_population'] = helpers.total_population(population_dataset)
            country_data['urban_rural_percentages'] = helpers.urban_rural_percentages(urban_rural_dataset)

            for section in sections:
                age_group_population_data[section] = {}
                age_groups = self.export_plan.data['ui_options'].get(section, {}).get('target_ages', [])
                age_group_population_data[section]['target_ages'] = age_groups
                age_group_population_data[section][
                    'male_target_age_population'
                ] = helpers.total_population_by_gender_age(
                    dataset=population_dataset, age_filter=age_groups, gender='male'
                )
                age_group_population_data[section][
                    'female_target_age_population'
                ] = helpers.total_population_by_gender_age(
                    dataset=population_dataset, age_filter=age_groups, gender='female'
                )
                age_group_population_data[section]['total_target_age_population'] = int(
                    age_group_population_data[section]['male_target_age_population']
                ) + int(age_group_population_data[section]['female_target_age_population'])

        context['country_data'] = country_data
        context['country_data']['population_age_data'] = age_group_population_data
        context['comtrade_data'] = comtrade_data
        return context


class FactbookDataContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        language_data = {}
        country_name = self.export_plan.export_country_name
        if country_name:
            language_data = helpers.get_cia_world_factbook_data(country=country_name, key='people,languages')

        context['language_data'] = language_data
        return context


class PDFContextProvider(BaseContextProvider):
    def get_context_provider_data(self, request, **kwargs):
        context = super().get_context_provider_data(request, **kwargs)
        processor = ExportPlanProcessor(self.export_plan.data)
        contact_dict = {'email': settings.GREAT_SUPPORT_EMAIL}
        if settings.PDF_STATIC_URL:
            # Based on AWS public dir
            pdf_statics_url = settings.PDF_STATIC_URL
        else:
            # Mostly used for local host
            host = request.get_host()
            pdf_statics_url = f'http://{host}{settings.STATIC_URL}'
        context.update(
            {
                'pdf_statics_url': pdf_statics_url,
                'export_plan': self.export_plan,
                'user': request.user,
                'sections': data.SECTION_TITLES,
                'calculated_pricing': processor.calculated_cost_pricing(),
                'total_funding': processor.calculate_total_funding(),
                'contact_detail': contact_dict,
            }
        )
        # GP2-2834 - Fix ordering of all EP lists to object pk (creation order)
        for item_list in [
            'business_trips',
            'company_objectives',
            'target_market_documents',
            'route_to_markets',
            'business_risks',
        ]:
            (context['export_plan'].data.get(item_list) or []).sort(key=lambda trip: trip.get('pk'))
        return context
