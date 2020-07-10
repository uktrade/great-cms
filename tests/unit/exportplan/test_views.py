from collections import OrderedDict
from datetime import datetime
from io import BytesIO
from unittest import mock
import json
import pytest

from freezegun import freeze_time
from PIL import Image, ImageDraw
from requests.exceptions import HTTPError

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.helpers import create_response
from exportplan import data, helpers
from directory_api_client.client import api_client


@pytest.fixture
def company_profile_data():
    return {
        'name': 'Cool Company',
        'is_publishable': True,
        'expertise_products_services': {},
        'expertise_countries': 'China',
        'expertise_industries': 'HR',
        'is_identity_check_message_sent': False,
        'is_published_find_a_supplier': False,
        'number': '1234567',
        'slug': 'cool-company',
        'created': '2012-06-15T13:45:30.00000Z',
        'modified': '2019-04-05T06:43:23.00000Z'
    }


def create_test_image(extension):
    image = Image.new('RGB', (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'This text is drawn on image')
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


@pytest.fixture(autouse=True)
def mock_update_company():
    patch = mock.patch.object(api_client.company, 'profile_update', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.mark.django_db
def test_export_plan_landing_page(client, exportplan_homepage, user, mock_get_company_profile, company_profile_data):
    mock_get_company_profile.return_value = company_profile_data
    client.force_login(user)

    response = client.get('/export-plan/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_plan_builder_landing_page(
    client, exportplan_dashboard, user, mock_get_company_profile, company_profile_data
):
    mock_get_company_profile.return_value = company_profile_data
    client.force_login(user)

    response = client.get('/export-plan/dashboard/')
    assert response.status_code == 200
    assert response.context['sections'] == data.SECTION_TITLES


@pytest.mark.django_db
@pytest.mark.parametrize('slug', set(data.SECTION_SLUGS) - {'target-markets', 'marketing-approach', 'objectives'})
@mock.patch.object(helpers, 'get_or_create_export_plan', mock.Mock(return_value={'brand_product_details': ''}))
def test_exportplan_sections(slug, client, user):
    client.force_login(user)

    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_or_create_export_plan', mock.Mock(return_value={}))
def test_exportplan_section_target_makret(client, user):
    client.force_login(user)

    response = client.get(reverse('exportplan:target-markets'))
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_or_create_export_plan', mock.Mock(return_value={}))
def test_exportplan_section_marketing_approach(client, user):
    client.force_login(user)

    response = client.get(reverse('exportplan:marketing-approach'))
    assert response.status_code == 200
    assert 'country' not in response.context_data
    assert 'united_kingdom' not in response.context_data
    assert 'age_range' not in response.context_data


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_or_create_export_plan', mock.Mock(return_value={'brand_product_details': ''}))
def test_exportplan_section_target_makret_country(client, user):
    client.force_login(user)

    response = client.get(reverse('exportplan:marketing-approach'), {'name': 'France', 'age_range': '30-34'})
    assert response.status_code == 200
    assert 'united_kingdom' in response.context_data
    assert 'country' in response.context_data
    assert 'age_range' in response.context_data
    assert response.context_data['country'].name
    assert response.context_data['country'].year_income
    assert response.context_data['country'].year_population
    assert response.context_data['country'].population
    assert response.context_data['country'].rural_percentage
    assert response.context_data['country'].urban_percentage
    assert response.context_data['country'].consumer_price_index
    assert response.context_data['age_range'].name
    assert response.context_data['age_range'].age_range
    assert response.context_data['age_range'].population_female
    assert response.context_data['age_range'].population_male


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@mock.patch('exportplan.helpers.get_exportplan')
@mock.patch('core.helpers.store_user_location')
def test_exportplan_target_markets(mock_user_location_create, mock_get_exportplan, client, user):
    client.force_login(user)

    explan_plan_data = {
        'country': 'Australia',
        'commodity_code': '220.850',
        'sectors': ['Automotive'],
        'target_markets': [
            {'country': 'China'},
        ],
        'rules_regulations': {
            'country_code': 'CHN',
        },
    }
    mock_get_exportplan.return_value = explan_plan_data

    response = client.get(reverse('exportplan:target-markets'))

    assert mock_get_exportplan.call_count == 1
    assert mock_get_exportplan.call_args == mock.call(user.session_id)

    assert response.context['target_markets'] == json.dumps(explan_plan_data['target_markets'])
    assert response.context['selected_sectors'] == json.dumps(explan_plan_data['sectors'])
    assert response.context['datenow'] == datetime.now()


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_exportplan')
@mock.patch.object(helpers, 'get_or_create_export_plan', return_value={'pk': 1, 'target_markets': []})
def test_update_export_plan_api_view(mock_get_or_create_export_plan, mock_update_exportplan, client, user):
    client.force_login(user)
    mock_update_exportplan.return_value = {'target_markets': [{'country': 'UK'}]}

    url = reverse('exportplan:api-update-export-plan')

    response = client.post(url, {'target_markets': ['China', 'India']})
    assert mock_get_or_create_export_plan.call_count == 1
    assert mock_get_or_create_export_plan.call_args == mock.call(user)
    assert response.status_code == 200

    assert mock_update_exportplan.call_count == 1
    assert mock_update_exportplan.call_args == mock.call(
        data=OrderedDict([('target_markets', [{'country': 'China'}, {'country': 'India'}])]),
        id=1,
        sso_session_id='123'
    )


@pytest.mark.django_db
def test_edit_logo_page_submmit_success(client, mock_update_company, user):
    client.force_login(user)
    url = reverse('exportplan:add-logo')
    data = {
        'logo': SimpleUploadedFile(
            name='image.png',
            content=create_test_image('png').read(),
            content_type='image/png',
        )
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == '/export-plan/dashboard/'
    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(
        sso_session_id=user.session_id,
        data={'logo': mock.ANY}
    )


@pytest.mark.django_db
def test_edit_logo_page_submmit_error(client, mock_update_company, user):
    client.force_login(user)
    url = reverse('exportplan:add-logo')
    data = {
        'logo': SimpleUploadedFile(
            name='image.png',
            content=create_test_image('png').read(),
            content_type='image/png',
        )
    }
    mock_update_company.return_value = create_response(status_code=400)

    with pytest.raises(HTTPError):
        client.post(url, data)


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_objective')
def test_update_objective_api_view(mock_update_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-update')

    objective = {'pk': 1, 'description': 'Some text', 'companyexportplan': 1}

    mock_update_objective.return_value = objective

    response = client.post(url, objective)

    assert mock_update_objective.call_count == 1
    assert response.status_code == 200
    assert mock_update_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_objective')
def test_create_objective_api_view(mock_create_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-create')

    objective = {'description': 'Some text', 'companyexportplan': 1}

    mock_create_objective.return_value = {'pk': 1, **objective}

    response = client.post(url, objective)

    assert mock_create_objective.call_count == 1
    assert response.status_code == 200
    assert mock_create_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_objective')
def test_delete_objective_api_view(mock_delete_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-delete')

    objective = {'pk': 1}

    mock_delete_objective.return_value = {}

    response = client.delete(url, objective, content_type='application/json')

    assert mock_delete_objective.call_count == 1
    assert response.status_code == 200
    assert mock_delete_objective.call_args == mock.call('123', objective)


@pytest.mark.django_db
@mock.patch.object(helpers, 'delete_objective')
def test_objectives_validation_delete(mock_delete_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-delete')

    objective = {}

    mock_delete_objective.return_value = {}

    response = client.delete(url, objective, content_type='application/json')

    assert mock_delete_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {'pk': ['This field is required.']}


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_objective')
def test_objectives_validation_update(mock_update_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-update')

    objective = {}

    mock_update_objective.return_value = {}

    response = client.post(url, objective)

    assert mock_update_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.'],
        'pk': ['This field is required.']
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_objective')
def test_objectives_validation_create(mock_create_objective, client, user):
    client.force_login(user)

    url = reverse('exportplan:api-objectives-create')

    objective = {}

    mock_create_objective.return_value = {}

    response = client.post(url, objective)

    assert mock_create_objective.call_count == 0
    assert response.status_code == 400
    assert response.json() == {
        'companyexportplan': ['This field is required.']
    }
