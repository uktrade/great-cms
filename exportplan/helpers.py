import pytz

from config import settings

from airtable import Airtable
from directory_api_client import api_client
from iso3166 import countries_by_alpha3


def create_export_plan(sso_session_id, exportplan_data):
    response = api_client.exportplan.exportplan_create(sso_session_id=sso_session_id, data=exportplan_data)
    response.raise_for_status()
    return response.json()


def get_exportplan_rules_regulations(sso_session_id):
    response = api_client.exportplan.exportplan_list(sso_session_id)
    response.raise_for_status()
    if response.json():
        return response.json()[0]['rules_regulations']


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


def get_madb_commodity_list():
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    commodity_name_set = set()
    for row in airtable.get_all(view='Grid view'):
        commodity_code = row['fields']['commodity_code']
        commodity_name = row['fields']['commodity_name']
        commodity_name_code = f'{commodity_name} - {commodity_code}'
        commodity_name_set.add((commodity_code, commodity_name_code))
    return commodity_name_set


def get_rules_and_regulations(country):
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    rules = airtable.search('country', country)
    if not rules:
        raise ValueError('No data found for country')
    return rules[0]['fields']


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


def serialize_exportplan_data(rules_regulations, user):
    target_markets = [{'country': rules_regulations['country']}]
    if user.company and user.company.expertise_countries_labels:
        target_markets = target_markets + [{'country': c} for c in user.company.expertise_countries_labels]
    exportplan_data = {
        'export_countries': [rules_regulations['country']],
        'export_commodity_codes': [rules_regulations['commodity_code']],
        'rules_regulations': rules_regulations,
        'target_markets': target_markets,


    }
    if settings.FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE:
        exportplan_data['sectors'] = ['food and drink']
    return exportplan_data


def get_or_create_export_plan(user):
    # This is a temp hook to create initial export plan. Once we have a full journey this can be removed
    export_plan = get_exportplan(user.session_id)
    if not export_plan:
        rules = get_rules_and_regulations('Australia')
        export_plan = create_export_plan(
            sso_session_id=user.session_id,
            exportplan_data=serialize_exportplan_data(rules_regulations=rules, user=user)
        )
    return export_plan


def create_objective(sso_session_id, data):
    response = api_client.exportplan.exportplan_objectives_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def update_objective(sso_session_id, data):
    response = api_client.exportplan.exportplan_objectives_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data)
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
    response = api_client.exportplan.route_to_market_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data)
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
    response = api_client.exportplan.route_to_market_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data)
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
