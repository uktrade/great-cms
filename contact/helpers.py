import requests
from django.urls import reverse_lazy

from directory_api_client import api_client
from directory_constants.choices import COUNTRY_CHOICES


def get_free_trade_agreements():
    response = api_client.dataservices.list_uk_free_trade_agreements()
    response.raise_for_status()
    return response.json()


def retrieve_regional_offices(postcode):
    response = api_client.exporting.lookup_regional_offices_by_postcode(postcode)
    response.raise_for_status()
    return response.json()


def retrieve_regional_office(postcode):
    all_offices = retrieve_regional_offices(postcode)
    regional_office = [office for office in all_offices if office['is_match']]
    return regional_office[0] if regional_office else None


def extract_regional_office_details(all_offices):
    matches = [office for office in all_offices if office['is_match']]
    formatted_office_details = format_office_details(matches)
    return formatted_office_details if formatted_office_details else None


def extract_other_offices_details(all_offices):
    other_offices = [office for office in all_offices if not office['is_match']]
    return format_office_details(other_offices)


def format_office_details(office_list):
    offices = []
    for office in office_list:
        address = office['address_street'].split(', ')
        address.append(office['address_city'])
        address.append(office['address_postcode'])
        office = {'address': '\n'.join(address), **office}
        offices.append(office)

    return offices if len(offices) > 0 else None


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


def retrieve_regional_office_email(postcode):
    try:
        office_details = retrieve_regional_offices(postcode)
    except requests.exceptions.RequestException:
        email = None
    else:
        matches = [office for office in office_details if office['is_match']]
        email = matches[0]['email'] if matches else None
    return email


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
            'notinlast12months': 'I have exported before but not in the last 12 months',
            'last12months': 'I have exported in the last 12 months',
            'noproduct': 'I do not have a product for export',
        },
    }

    return field_value_mappings.get(key).get(form_data.get(key))


def get_steps(form_data, second_step_edit_page, markets):
    markets_mapping = dict(
        COUNTRY_CHOICES + [('not_specific_country', 'My query is not related to a specific country')]
    )

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
                ('First name', form_data.get('first_name')),
                ('Last name', form_data.get('last_name')),
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
