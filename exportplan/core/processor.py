from collections import OrderedDict

from dateutil import parser
from django.utils.text import slugify
from rest_framework.fields import ListField
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
        (slugify(data.BUSINESS_RISK), 'business_risks'),
    ]

    def __init__(self, data):
        self.data = data
        self.seralizer = serializers.ExportPlanSerializer(data=self.data)
        self.seralizer.is_valid()

    def calculate_ep_section_progress(self):
        progress = []
        sections = dict(data.SECTIONS)
        for field_map in self.FIELD_NAME_MAP:
            total = 1
            populated = 0
            field_class = self.seralizer.fields[field_map[1]]
            section_key = sections[field_map[0]]['url']
            if isinstance(field_class, Serializer):
                total = len(getattr(field_class, 'fields'))
                for field_name, field_type in getattr(field_class, 'fields').items():
                    if isinstance(field_type, ListField) and self.has_items(field_name):
                        populated += 1
                    elif self.has_value(field_map[1], field_name):
                        populated += 1
            elif isinstance(field_class, ListField) and self.has_items(field_name):
                populated += 1
            progress.append({'total': total, 'populated': populated, 'url': section_key})
        return progress

    def has_items(self, field_name):
        return True if len(self.seralizer.initial_data.get(field_name, [])) > 0 else False

    def has_value(self, field_name, sub_field_name):
        field_value = ''
        if sub_field_name in self.seralizer.initial_data.get(field_name, {}):
            field_value = self.seralizer.initial_data[field_name][sub_field_name]
        return False if field_value == '' else True

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
        progress_items = OrderedDict(
            sorted(
                self.data.get('ui_progress', {}).items(),
                reverse=True,
                key=lambda item: parser.parse(
                    item[1].get('date_last_visited', '1970-01-01'),
                ),
            )
        )
        completed = dict(filter(lambda i: i[1].get('is_complete', False) is True, progress_items.items()))
        uncompleted = dict(filter(lambda i: i[1].get('is_complete', False) is False, progress_items.items()))
        exportplan_completed = True if len(completed) == len(data.SECTION_SLUGS) else False

        if len(uncompleted):
            # Next section is last visited uncompleted page
            next_section_key = list(uncompleted.keys())[0]
        elif len(completed) and not exportplan_completed:
            # Lets find next section in export plan
            for section in data.SECTION_SLUGS:
                if not completed.get(section):
                    next_section_key = section
                    break
        else:
            # Default to first page in export plan
            next_section_key = data.SECTION_SLUGS[0]

        next_section = data.SECTIONS.get(next_section_key, {})

        return {
            'sections_completed': len(completed),
            'exportplan_completed': exportplan_completed,
            'sections_total': len(data.SECTION_SLUGS),
            'percentage_completed': len(completed) / len(data.SECTION_SLUGS) if len(completed) > 0 else 0,
            'section_progress': self.calculate_ep_section_progress(),
            'next_section': {
                'title': next_section.get('title', ''),
                'url': next_section.get('url', ''),
                'image': next_section.get('image', ''),
            },
        }
