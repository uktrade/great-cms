from unittest import mock

import pytest
from django.core.files import File

from directory_api_client import api_client
from exportplan.core import helpers
from tests.helpers import create_response


@mock.patch.object(api_client.exportplan, 'create')
def test_create_export_plan(mock_exportplan_create):
    export_plan_data = {'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}
    mock_exportplan_create.return_value = create_response(status_code=201)
    helpers.create_export_plan(sso_session_id=123, data=export_plan_data)

    assert mock_exportplan_create.call_count == 1
    assert mock_exportplan_create.call_args == mock.call(
        data={'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}, sso_session_id=123
    )


@mock.patch.object(api_client.exportplan, 'delete_export_plan')
def test_delete_export_plan(mock_exportplan_delete_export_plan):
    mock_exportplan_delete_export_plan.return_value = create_response(status_code=200)
    helpers.delete_export_plan(sso_session_id=123, id=1)
    assert mock_exportplan_delete_export_plan.call_count == 1
    assert mock_exportplan_delete_export_plan.call_args == mock.call(sso_session_id=123, id=1)


def test_country_code_iso3_to_iso2():
    assert helpers.country_code_iso3_to_iso2('CHN') == 'CN'


def test_country_code_iso3_to_iso2_not_found():
    assert helpers.country_code_iso3_to_iso2('XNY') is None


def test_get_timezone():
    assert helpers.get_timezone('CHN') == 'Asia/Shanghai'


def test_get_local_time_not_found():
    assert helpers.get_timezone('XS') is None


@mock.patch.object(api_client.exportplan, 'update')
def test_update_export_plan(mock_exportplan_update):
    export_plan_data = {'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}
    mock_exportplan_update.return_value = create_response(status_code=200, json_body=export_plan_data)
    helpers.update_exportplan(sso_session_id=123, id=1, data=export_plan_data)

    assert mock_exportplan_update.call_count == 1
    assert mock_exportplan_update.call_args == mock.call(
        data={'Country': 'UK', 'Commodity code': 100, 'rules': {'rule1': '12343'}}, id=1, sso_session_id=123
    )


def test_get_cia_world_factbook_data(mock_api_get_cia_world_factbook_data, cia_factbook_data):
    response = helpers.get_cia_world_factbook_data(country='United Kingdom', key='people,languages')
    assert mock_api_get_cia_world_factbook_data.call_count == 1
    assert mock_api_get_cia_world_factbook_data.call_args == mock.call(
        country='United Kingdom', data_key='people,languages'
    )
    assert response == cia_factbook_data


@mock.patch.object(api_client.exportplan, 'model_object_create')
def test_model_object_create(mock_model_object_create):
    data = {'note': 'new note', 'companyexportplan': 1}
    mock_model_object_create.return_value = create_response(data)

    response = helpers.create_model_object(123, data, 'BusinessTrips')

    assert mock_model_object_create.call_count == 1
    assert mock_model_object_create.call_args == mock.call(data=data, sso_session_id=123, model_name='BusinessTrips')
    assert response == data


@mock.patch.object(api_client.exportplan, 'model_object_update')
def test_model_object_update(mock_update_model_object):
    data = {'pk': 1, 'note': 'update me', 'companyexportplan': 1}
    mock_update_model_object.return_value = create_response(data)

    response = helpers.update_model_object(sso_session_id=123, data=data, model_name='BusinessTrips')

    assert mock_update_model_object.call_count == 1
    assert mock_update_model_object.call_args == mock.call(
        data=data, id=data['pk'], sso_session_id=123, model_name='BusinessTrips'
    )
    assert response == data


@mock.patch.object(api_client.exportplan, 'model_object_delete')
def test_model_object_delete(mock_delete_model_object):
    data = {'pk': 1}
    mock_delete_model_object.return_value = create_response(data)

    response = helpers.delete_model_object(sso_session_id=123, data=data, model_name='BusinessTrips')

    assert mock_delete_model_object.call_count == 1
    assert mock_delete_model_object.call_args == mock.call(
        id=data['pk'], sso_session_id=123, model_name='BusinessTrips'
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_lesson_details(curated_list_pages_with_lessons):
    lesson_list = ['lesson-a1', 'lesson-a2', 'lesson-b1']
    lessons = helpers.get_lesson_details(lesson_list)
    assert lessons == {
        'lesson-a1': {
            'category': 'Some title',
            'title': 'Lesson A1',
            'duration': '2 hour 45 min',
            'url': None,
        },
        'lesson-a2': {
            'category': 'Some title',
            'title': 'Lesson A2',
            'duration': '12 min',
            'url': None,
        },
        'lesson-b1': {
            'category': 'Some title b',
            'title': 'Lesson b1',
            'duration': '10 min',
            'url': None,
        },
    }


@pytest.mark.django_db
def test_get_lesson_details_empty(curated_list_pages_with_lessons):
    lesson_list = []
    lessons = helpers.get_lesson_details(lesson_list)
    assert lessons == {}


@pytest.mark.django_db
def test_get_lesson_details_no_found(curated_list_pages_with_lessons):
    lesson_list = ['ewkjhewfk']
    lessons = helpers.get_lesson_details(lesson_list)
    assert lessons == {}


@mock.patch.object(api_client.dataservices, 'get_society_data_by_country')
def test_get_society_data_by_country(mock_society_data_by_country):
    data = {'country': 'United Kingdom', 'languages': [{'name': 'English'}]}

    mock_society_data_by_country.return_value = create_response(data)
    response = helpers.get_society_data_by_country(countries='United Kingdom')
    assert mock_society_data_by_country.call_count == 1
    assert mock_society_data_by_country.call_args == mock.call(countries='United Kingdom')
    assert response == data


@pytest.mark.parametrize(
    'ui_options_data,',
    [
        {'target-market': {'target_ages': ['30-40']}},
        {'target-market': {'target_ages': None}},
        {'target-market': None},
        None,
        {'target-market-research': {'target_ages': ['21-15']}},
    ],
)
@mock.patch.object(api_client.exportplan, 'update')
def test_update_ui_options_target_ages(mock_update_export_plan, export_plan_data, ui_options_data):
    export_plan_data.update({'ui_options': ui_options_data})
    helpers.update_ui_options_target_ages(
        sso_session_id=1, target_ages=['21-15'], export_plan=export_plan_data, section_name='target-market'
    )
    assert mock_update_export_plan.call_count == 1
    assert mock_update_export_plan.call_args == mock.call(
        sso_session_id=1, id=1, data={'ui_options': {'target-market': {'target_ages': ['21-15']}}}
    )


@mock.patch.object(api_client.exportplan, 'pdf_upload')
def test_upload_exportplan_pdf(mock_upload_pdf, export_plan_data):
    mock_file = mock.Mock(spec=File)
    helpers.upload_exportplan_pdf(sso_session_id=1, exportplan_id=5, file=mock_file)
    assert mock_upload_pdf.call_count == 1
    assert mock_upload_pdf.call_args == mock.call(
        sso_session_id=1, data={'companyexportplan': 5, 'pdf_file': mock_file}
    )


@pytest.mark.parametrize(
    'age_filter, sex, total',
    [
        [['0-14'], 'female', 5891000],
        [['65+'], 'male', 0],
        [['0-14', '15-19'], 'female', 7877000],
        [[], 'male', 0],
    ],
)
def test_total_population_by_gender_age(age_filter, sex, total):
    ds = {
        'PopulationData': [
            {
                'year': 2020,
                'gender': 'male',
                '0-4': 1770,
                '5-9': 1912,
                '60-64': 2070,
            },
            {
                'year': 2020,
                'gender': 'female',
                '0-4': 1850,
                '5-9': 1996,
                '10-14': 2045,
                '15-19': 1986,
                '20-24': 1869,
            },
        ]
    }
    assert helpers.total_population_by_gender_age(ds['PopulationData'], age_filter, sex) == total


def test_get_total_population(multiple_country_data):
    assert helpers.total_population(multiple_country_data['NL']['PopulationData']) == 20000


def test_urban_rural_percentages(multiple_country_data):
    assert helpers.urban_rural_percentages(multiple_country_data['NL']['PopulationUrbanRural']) == {
        'rural_percentage': 0.6667,
        'total_population': 300,
        'urban_percentage': 0.3333,
    }
