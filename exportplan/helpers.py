from decimal import Decimal

import pytz
from iso3166 import countries_by_alpha3

from core import models
from directory_api_client import api_client
from exportplan import data


def create_export_plan(sso_session_id, exportplan_data):
    response = api_client.exportplan.exportplan_create(sso_session_id=sso_session_id, data=exportplan_data)
    response.raise_for_status()
    return response.json()


def get_exportplan(sso_session_id):
    response = api_client.exportplan.exportplan_list(sso_session_id)
    response.raise_for_status()
    parsed = response.json()
    if parsed:
        return parsed[0]


def update_exportplan(sso_session_id, id, data):
    response = api_client.exportplan.exportplan_update(sso_session_id=sso_session_id, id=id, data=data)
    response.raise_for_status()
    return response.json()


def get_exportplan_marketdata(country_code):
    # This is a temp wrapper for MVP as we finalise the source(s) this should move to backend
    exportplan_marketdata = {}
    exportplan_marketdata['timezone'] = get_timezone(country_code)

    exportplan_response = api_client.dataservices.get_corruption_perceptions_index(country_code)
    exportplan_response.raise_for_status()
    exportplan_marketdata['corruption_perceptions_index'] = exportplan_response.json()

    marketdata_response = api_client.dataservices.get_ease_of_doing_business(country_code)
    marketdata_response.raise_for_status()
    exportplan_marketdata['easeofdoingbusiness'] = marketdata_response.json()
    return exportplan_marketdata


def country_code_iso3_to_iso2(iso3_country_code):
    if countries_by_alpha3.get(iso3_country_code):
        return countries_by_alpha3[iso3_country_code].alpha2


def get_timezone(country_code):
    iso3_country_code = country_code_iso3_to_iso2(country_code)
    if iso3_country_code and pytz.country_timezones(iso3_country_code):
        return pytz.country_timezones(iso3_country_code)[0]


def get_comtrade_last_year_import_data(commodity_code, country):
    response = api_client.dataservices.get_last_year_import_data(commodity_code=commodity_code, country=country)
    response.raise_for_status()
    return response.json()


def get_comtrade_historical_import_data(commodity_code, country):
    response = api_client.dataservices.get_historical_import_data(commodity_code=commodity_code, country=country)
    response.raise_for_status()
    return response.json()


def get_population_data_by_country(countries):
    response = api_client.dataservices.get_population_data_by_country(countries=countries)
    response.raise_for_status()
    return response.json()


def get_recommended_countries(sso_session_id, sectors):
    response = api_client.personalisation.recommended_countries_by_sector(sso_session_id=sso_session_id, sector=sectors)
    response.raise_for_status()
    parsed = response.json()
    if parsed:
        for item in parsed:
            country = item['country'].title()
            item['country'] = country
        return parsed
    return []


def serialize_exportplan_data(user):
    target_markets = []
    if user.company and user.company.expertise_countries_labels:
        target_markets = target_markets + [{'country': c} for c in user.company.expertise_countries_labels]
        export_plan_data = {
            'target_markets': target_markets,
        }
    else:
        export_plan_data = {}
    return export_plan_data


def get_or_create_export_plan(user):
    # This is a temp hook to create initial export plan. Once we have a full journey this can be removed
    export_plan = get_exportplan(user.session_id)
    if not export_plan:
        export_plan = create_export_plan(
            sso_session_id=user.session_id, exportplan_data=serialize_exportplan_data(user=user)
        )
    return export_plan


def create_objective(sso_session_id, data):
    response = api_client.exportplan.exportplan_objectives_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def update_objective(sso_session_id, data):
    response = api_client.exportplan.exportplan_objectives_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data
    )
    response.raise_for_status()
    return response.json()


def delete_objective(sso_session_id, data):
    response = api_client.exportplan.exportplan_objectives_delete(sso_session_id=sso_session_id, id=data['pk'])
    response.raise_for_status()
    return response


def create_route_to_market(sso_session_id, data):
    response = api_client.exportplan.route_to_market_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def update_route_to_market(sso_session_id, data):
    response = api_client.exportplan.route_to_market_update(sso_session_id=sso_session_id, id=data['pk'], data=data)
    response.raise_for_status()
    return response.json()


def delete_route_to_market(sso_session_id, data):
    response = api_client.exportplan.route_to_market_delete(sso_session_id=sso_session_id, id=data['pk'])
    response.raise_for_status()
    return response


def create_target_market_documents(sso_session_id, data):
    response = api_client.exportplan.target_market_documents_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def update_target_market_documents(sso_session_id, data):
    response = api_client.exportplan.target_market_documents_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data
    )
    response.raise_for_status()
    return response.json()


def delete_target_market_documents(sso_session_id, data):
    response = api_client.exportplan.target_market_documents_delete(sso_session_id=sso_session_id, id=data['pk'])
    response.raise_for_status()
    return response


def get_country_data(country):
    response = api_client.dataservices.get_country_data(country)
    response.raise_for_status()
    return response.json()


def get_global_demographic_data(country):
    country_data = get_country_data(country)
    factbook_data = get_cia_world_factbook_data(country=country, key='people,languages')
    return {**country_data, **factbook_data}


def get_cia_world_factbook_data(country, key):
    response = api_client.dataservices.get_cia_world_factbook_data(country=country, data_key=key)
    response.raise_for_status()
    return response.json()


def get_population_data(country, target_ages):
    response = api_client.dataservices.get_population_data(country=country, target_ages=target_ages)
    response.raise_for_status()
    return response.json()


def get_check_duties_link(exportplan):
    # TODO Once requirements have been defined pick country code from export plan
    url = 'https://www.check-duties-customs-exporting-goods.service.gov.uk/'
    return url


def get_all_lesson_details():
    lessons = {}
    for lesson in models.DetailPage.objects.live().specific():
        lessons[lesson.slug] = {
            'topic_name': lesson.topic_title,
            'title': lesson.title,
            'estimated_read_duration': lesson.estimated_read_duration,
            'url': lesson.url,
        }
    return lessons


def get_current_url(slug, export_plan):
    current_url = data.SECTIONS[slug]
    current_url.pop('country_required', None)
    current_url.pop('product_required', None)
    if slug in data.COUNTRY_REQUIRED:
        if not export_plan.get('export_countries') or len(export_plan['export_countries']) == 0:
            current_url['country_required'] = True
    if slug in data.PRODUCT_REQUIRED:
        if not export_plan.get('export_commodity_codes') or len(export_plan['export_commodity_codes']) == 0:
            current_url['product_required'] = True
    return current_url


def update_ui_options_target_ages(sso_session_id, target_ages, export_plan, section_name):
    if (not export_plan.get('ui_options') or not export_plan['ui_options'].get(section_name, {})) or (
        export_plan['ui_options'].get(section_name, {}).get('target_ages') != target_ages
    ):
        update_exportplan(
            sso_session_id=sso_session_id,
            id=export_plan['pk'],
            data={'ui_options': {section_name: {'target_ages': target_ages}}},
        )


def calculate_cost_pricing(exportplan):
    calculated_dict = {}
    netprice = exportplan.get('total_cost_and_price', {}).get('net_price')
    final_cost_per_unit = exportplan.get('total_cost_and_price', {}).get('final_cost_per_unit')
    no_of_unit = exportplan.get('total_cost_and_price', {}).get('units_to_export_first_period', {}).get('value')
    if netprice and final_cost_per_unit:
        profit_per_unit = Decimal(final_cost_per_unit) - Decimal(netprice)
        calculated_dict.update({'profit_per_unit': profit_per_unit})
        if no_of_unit:
            potential_total_profit = profit_per_unit * Decimal(no_of_unit)
            calculated_dict.update({'potential_total_profit': potential_total_profit})
    return {'calculated_cost_pricing': calculated_dict}
