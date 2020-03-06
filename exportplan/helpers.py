from airtable import Airtable
from directory_api_client import api_client


def create_export_plan(sso_session_id, exportplan_data):
    response = api_client.exportplan.exportplan_create(sso_session_id=sso_session_id, data=exportplan_data)
    response.raise_for_status()
    return response.json()


def get_exportplan_rules_regulations(sso_session_id):
    response = api_client.exportplan.exportplan_list(sso_session_id)
    response.raise_for_status()
    if response.json():
        return response.json()[0]['rules_regulations']


def get_madb_country_list():
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    airtable_data = airtable.get_all(view='Grid view')
    country_list = [c['Country'] for c in [f['fields'] for f in airtable_data]]
    return list(zip(country_list, country_list))


def get_madb_commodity_list():
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    commodity_name_set = set()
    for row in airtable.get_all(view='Grid view'):
        commodity_code = row['fields']['Commodity code']
        commodity_name = row['fields']['Commodity Name']
        commodity_name_code = f'{commodity_name} - {commodity_code}'
        commodity_name_set.add((commodity_code, commodity_name_code))
    return commodity_name_set


def get_rules_and_regulations(country):
    airtable = Airtable('appcxR2dZGyugfvyd', 'CountryDBforGIN')
    rules = airtable.search('country', country)
    if rules:
        return rules[0]['fields']
