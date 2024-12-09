import logging

from django.urls import reverse_lazy

from contact.models import DPEFormToZendeskFieldMapping
from directory_api_client import api_client
from directory_constants.choices import COUNTRY_CHOICES

logger = logging.getLogger(__name__)


def get_free_trade_agreements():
    response = api_client.dataservices.list_uk_free_trade_agreements()
    response.raise_for_status()
    return response.json()


def build_export_opportunites_guidance_url(slug):
    return reverse_lazy(
        'contact:contact-us-export-opportunities-guidance',
        kwargs={'slug': slug},
    )


def build_account_guidance_url(slug):
    return reverse_lazy(
        'contact:contact-us-great-account-guidance',
        kwargs={'slug': slug},
    )


def get_export_support_field_mappings(key, form_data):
    field_value_mappings = {
        'business_type': {
            'limitedcompany': 'UK private or public limited company',
            'other': 'Other type of UK organisation',
            'soletrader': 'Sole trader or private individual',
        },
        'type': {
            'privatelimitedcompany': 'Private limited company',
            'publiclimitedcompany': 'Public limited company',
            'soletrader': 'Sole trader',
            'limitedliability': 'Limited liability partnership',
            'notcurrentlytrading': 'Not currently trading',
            'closedbusiness': 'Close business',
            'other': 'Other',
            'cse': 'Charity / Social enterprise',
            'university': 'University',
            'othereduinst': 'Other educational institute',
            'partnership': 'Partnership',
            'privateindividual': 'Private individual',
        },
        'annual_turnover': {
            '<85k': 'Below £85,000 (Below VAT threshold)',
            '85k-499.000k': '£85,000 up to £499,000',
            '50k-1999.999k': '£500,000 up to £1,999,999',
            '2m-4999.999k': '£2 million up to £4,999,999',
            '5m-9999.999k': '£5 million up to £9,999,999',
            '10m': 'Over £10,000,000',
            'dontknow': "I don't know",
            'prefernottosay': "I'd prefer not to say",
        },
        'number_of_employees': {
            '1-9': '1 to 9',
            '10-49': '10 to 49',
            '50-249': '50 to 249',
            '250-499': '250 to 499',
            '500plus': 'More than 500',
        },
        'about_your_experience': {
            'neverexported': """I have never exported but have a product suitable or that
            could be developed for export""",
            'notinlast12months': 'I have exported before but not in the last 12 months',  # /PS-IGNORE
            'last12months': 'I have exported in the last 12 months',  # /PS-IGNORE
            'noproduct': 'I do not have a product for export',
        },
    }

    return field_value_mappings.get(key).get(form_data.get(key))


def get_steps(form_data, second_step_edit_page, markets):
    markets_mapping = dict(COUNTRY_CHOICES + [('notspecificcountry', 'My query is not related to a specific country')])

    return [
        {
            'title': 'Contact us',
            'answers': [
                ('Business type', get_export_support_field_mappings('business_type', form_data)),
                ('Business name', form_data.get('business_name')),
                ('Company registration number (optional)', form_data.get('company_registration_number')),
                ('Business postcode', form_data.get('business_postcode')),
            ],
            'change_url': reverse_lazy('contact:export-support-edit'),
            'change_text': 'Amend contact us section',
        },
        {
            'title': 'About your business',
            'answers': [
                ('Type of company', get_export_support_field_mappings('type', form_data)),
                ('Annual turnover', get_export_support_field_mappings('annual_turnover', form_data)),
                ('Number of employees', get_export_support_field_mappings('number_of_employees', form_data)),
                (
                    'What is your sector?',
                    ', '.join(
                        [
                            sector
                            for sector in [
                                form_data.get('sector_primary'),
                                form_data.get('sector_primary_other '),
                                form_data.get('sector_secondary'),
                                form_data.get('sector_tertiary'),
                            ]
                            if sector
                        ]
                    ),
                ),
            ],
            'change_url': second_step_edit_page,
            'change_text': 'Amend about your business section',
        },
        {
            'title': 'About you',
            'answers': [
                ('First name', form_data.get('first_name')),  # /PS-IGNORE
                ('Last name', form_data.get('last_name')),  # /PS-IGNORE
                ('Job title', form_data.get('job_title')),
                ('UK telephone number', form_data.get('uk_telephone_number')),
                ('Email address', form_data.get('email')),
            ],
            'change_url': reverse_lazy('contact:export-support-step-3-edit'),
            'business_name': form_data.get('business_name'),
            'change_text': 'Amend about you section',
        },
        {
            'title': 'About your product or service',
            'answers': [
                ('Product or service', form_data.get('product_or_service_1')),
                ('Second product or service', form_data.get('product_or_service_2')),
                ('Third product or service', form_data.get('product_or_service_3')),
                ('Fourth product or service', form_data.get('product_or_service_4')),
                ('Fifth product or service', form_data.get('product_or_service_5')),
            ],
            'change_url': reverse_lazy('contact:export-support-step-4-edit'),
            'change_text': 'Amend about your product or service section',
        },
        {
            'title': 'About your export markets',
            'answers': [
                ('Export markets', ', '.join([markets_mapping[market] for market in markets if market])),
            ],
            'change_url': reverse_lazy('contact:export-support-step-5-edit'),
            'change_text': 'Amend about your export markets section',
        },
        {
            'title': 'About your enquiry',
            'answers': [
                ('Your enquiry', form_data.get('enquiry')),
                ('About your export experience', get_export_support_field_mappings('about_your_experience', form_data)),
            ],
            'change_url': reverse_lazy('contact:export-support-step-6-edit'),
            'change_text': 'Amend about your enquiry section',
        },
    ]


def get_field_zendesk_mapping_value(mapping_obj, field, form_data):
    if mapping_obj.dpe_form_value_to_zendesk_field_value is not None:
        return mapping_obj.dpe_form_value_to_zendesk_field_value[form_data[field]]
    elif field == 'markets':
        markets_long_form = [country[1] for country in COUNTRY_CHOICES if country[0] in form_data[field]]
        mapped_value_markets = [f"{country.lower().replace(' ', '_')}__ess_export" for country in markets_long_form]

        if 'tunisia__ess_export' in mapped_value_markets:
            return [val.replace('tunisia__ess_export', 'unisia__ess_export') for val in mapped_value_markets]

        return mapped_value_markets
    elif field == 'sector_primary':
        # maps all l1 sectors (sector_primary, sector_secondary, sector_tertiary)
        return [
            f"{sector.lower().replace(',', '').replace(' ', '_')}__ess_sector_l1"
            for k, sector in form_data.items()
            if 'sector' in k
        ]
    else:
        return form_data[field]


def populate_custom_fields(form_data):
    result = {**form_data}
    result['_custom_fields'] = []
    for field in form_data.keys():
        if DPEFormToZendeskFieldMapping.objects.filter(dpe_form_field_id=field).exists():
            mapping_obj = DPEFormToZendeskFieldMapping.objects.get(dpe_form_field_id=field)

            try:
                result['_custom_fields'].append(
                    {mapping_obj.zendesk_field_id: get_field_zendesk_mapping_value(mapping_obj, field, form_data)}
                )
            except Exception as e:
                logger.error(e)

    return result


def dpe_clean_submission_for_zendesk(submission_data: dict):
    sorted_submission = dpe_sort_submission_data(submission_data)
    return dpe_map_fields_to_human_readable_values(sorted_submission)


def dpe_sort_submission_data(submission_data_unsorted: dict):
    priority = [
        'enquiry',
        'first_name',
        'last_name',
        'job_title',
        'uk_telephone_number',
        'email',
        'business_name',
        'business_type',
        'business_postcode',
        'company_registration_number',
    ]

    sorted = {field: submission_data_unsorted.get(field) for field in priority}
    unsorted = {field: value for field, value in submission_data_unsorted.items() if field not in priority}

    return {**sorted, **unsorted}


def dpe_map_fields_to_human_readable_values(submission_data: dict):
    fields_to_map = ['business_type', 'type', 'annual_turnover', 'number_of_employees', 'about_your_experience']
    result = {**submission_data}

    result.update({field: get_export_support_field_mappings(field, submission_data) for field in fields_to_map})

    return result
