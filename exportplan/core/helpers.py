import pytz
from iso3166 import countries_by_alpha3

from core import models
from core.templatetags.content_tags import format_timedelta
from directory_api_client import api_client
from exportplan.core.processor import ExportPlanProcessor


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


def country_code_iso3_to_iso2(iso3_country_code):
    if countries_by_alpha3.get(iso3_country_code):
        return countries_by_alpha3[iso3_country_code].alpha2


def get_timezone(country_code):
    iso3_country_code = country_code_iso3_to_iso2(country_code)
    if iso3_country_code and pytz.country_timezones(iso3_country_code):
        return pytz.country_timezones(iso3_country_code)[0]


def get_population_data_by_country(countries):
    response = api_client.dataservices.get_population_data_by_country(countries=countries)
    response.raise_for_status()
    return response.json()


def get_society_data_by_country(countries):
    response = api_client.dataservices.get_society_data_by_country(countries=countries)
    response.raise_for_status()
    return response.json()


def get_or_create_export_plan(user):
    # This is a temp hook to create initial export plan. Once we have a full journey this can be removed
    export_plan = get_exportplan(user.session_id)
    if not export_plan:
        # This currently creates an empty export plan
        export_plan = create_export_plan(sso_session_id=user.session_id, exportplan_data={})
    return export_plan


def get_cia_world_factbook_data(country, key):
    response = api_client.dataservices.get_cia_world_factbook_data(country=country, data_key=key)
    response.raise_for_status()
    return response.json()


def get_population_data(country, target_ages):
    response = api_client.dataservices.get_population_data(country=country, target_ages=target_ages)
    response.raise_for_status()
    return response.json()


def get_lesson_details(lessons):
    lessons_details = {}
    if len(lessons) > 0:
        for lesson in models.DetailPage.objects.live().filter(slug__in=lessons):
            lessons_details[lesson.slug] = {
                'category': lesson.topic_title,
                'title': lesson.title,
                'duration': format_timedelta(lesson.estimated_read_duration),
                'url': lesson.url,
            }
    return lessons_details


def update_ui_options_target_ages(sso_session_id, target_ages, export_plan, section_name):
    if (not export_plan.get('ui_options') or not export_plan['ui_options'].get(section_name, {})) or (
        export_plan['ui_options'].get(section_name, {}).get('target_ages') != target_ages
    ):
        update_exportplan(
            sso_session_id=sso_session_id,
            id=export_plan['pk'],
            data={'ui_options': {section_name: {'target_ages': target_ages}}},
        )


def create_model_object(sso_session_id, data, model_name):
    response = api_client.exportplan.model_object_create(
        sso_session_id=sso_session_id, data=data, model_name=model_name
    )
    response.raise_for_status()
    return response.json()


def update_model_object(sso_session_id, model_name, data):
    response = api_client.exportplan.model_object_update(
        sso_session_id=sso_session_id, id=data['pk'], data=data, model_name=model_name
    )
    response.raise_for_status()
    return response.json()


def delete_model_object(sso_session_id, model_name, data):
    response = api_client.exportplan.model_object_delete(
        sso_session_id=sso_session_id, id=data['pk'], model_name=model_name
    )
    response.raise_for_status()
    return response


def values_to_labels(values, choices):
    return ', '.join([choices.get(item) for item in values if item in choices])


def upload_exportplan_pdf(sso_session_id, exportplan_id, file):
    data = {'companyexportplan': exportplan_id, 'pdf_file': file}
    response = api_client.exportplan.pdf_upload(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response.json()


def get_exportplan_list(sso_session_id):
    response = api_client.exportplan.exportplan_detail_list(sso_session_id)
    response.raise_for_status()
    exportplan_list = response.json()
    for ep in exportplan_list:
        # On list page we need to know sections complete only EP processor can calculate this
        # Move this to an easy method TODO
        ep['calculated_progress'] = ExportPlanProcessor(ep).calculate_ep_progress()

    return exportplan_list
