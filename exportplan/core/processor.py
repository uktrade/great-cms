from django.utils.text import slugify
from rest_framework.serializers import Serializer

from . import data, serializers


class ExportPlanProcessor:
    """
    Processes requests for exportplan
    """

    FIELD_NAME_MAP = [
        (slugify(data.ABOUT_YOUR_BUSINESS), 'about_your_business'),
        (slugify(data.OBJECTIVES), 'objectives'),
        (slugify(data.TARGET_MARKETS_RESEARCH), 'target_markets_research'),
        (slugify(data.ADAPTATION_TARGET_MARKET), 'adaptation_target_market'),
        (slugify(data.MARKETING_APPROACH), 'marketing_approach'),
        (slugify(data.COSTS_AND_PRICING), 'total_cost_and_price'),
        (slugify(data.GETTING_PAID), 'getting_paid'),
        (slugify(data.FUNDING_AND_CREDIT), 'funding_and_credit'),
        (slugify(data.TRAVEL_AND_BUSINESS_POLICIES), 'travel_business_policies'),
        (slugify(data.BUSINESS_RISK), 'travel_business_policies'),
    ]

    def __init__(self, data):
        self.data = data
        self.seralizer = serializers.ExportPlanSerializer(data=self.data)
        self.seralizer.is_valid()

    def calculate_ep_section_progress(self):
        progress = []
        sections = dict(data.SECTIONS)
        for field_map in self.FIELD_NAME_MAP:
            total = 0
            populated = 0
            field_class = self.seralizer.fields[field_map[1]]
            section_key = sections[field_map[0]]['url']
            if isinstance(field_class, Serializer):
                total = len(getattr(field_class, 'fields'))
                for field in getattr(field_class, 'fields'):
                    if self.seralizer.initial_data.get(field_map[1], {}).get(field):
                        populated += 1
            progress.append({'total': total, 'populated': populated, 'url': section_key})
        return progress

    def build_current_url(self, slug):
        current_url = data.SECTIONS[slug]
        current_url.pop('country_required', None)
        current_url.pop('product_required', None)
        if slug in data.COUNTRY_REQUIRED:
            if not self.data.get('export_countries') or len(self.data['export_countries']) == 0:
                current_url['country_required'] = True
        if slug in data.PRODUCT_REQUIRED:
            if not self.data.get('export_commodity_codes') or len(self.data['export_commodity_codes']) == 0:
                current_url['product_required'] = True
        current_url['is_complete'] = self.data.get('ui_progress', {}).get(slug, {}).get('is_complete', False)
        return current_url

    def build_export_plan_sections(self):
        sections = data.SECTIONS
        for slug, values in sections.items():
            values['is_complete'] = self.data.get('ui_progress', {}).get(slug, {}).get('is_complete', False)
        return list(sections.values())

    def calculated_cost_pricing(self):
        calculated_pricing = serializers.ExportPlanSerializer(data=self.data).calculate_cost_pricing
        return {'calculated_cost_pricing': calculated_pricing}

    def calculate_total_funding(self):
        total_funding = serializers.ExportPlanSerializer(data=self.data).calculate_total_funding
        return {'calculated_total_funding': total_funding}

    def calculate_ep_progress(self):
        progress_items = self.data.get('ui_progress', {})
        completed = [True for v in progress_items.values() if v.get('is_complete')]
        return {
            'sections_completed': len(completed),
            'sections_total': len(data.SECTION_SLUGS),
            'percentage_completed': len(completed) / len(data.SECTION_SLUGS) if len(completed) > 0 else 0,
            'section_progress': self.calculate_ep_section_progress(),
        }
