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


@pytest.fixture(autouse=True)
def export_plan_data():
    return {
        'about_your_business': '',
        'target_markets_research': ''
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
@pytest.mark.parametrize('slug', set(data.SECTION_SLUGS) - {'marketing-approach', 'objectives'})
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_sections(mock_get_create_exportplan, export_plan_data, slug, client, user):
    mock_get_create_exportplan.return_value = export_plan_data
    client.force_login(user)

    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_section_marketing_approach(mock_get_create_export_plan, client, user):
    client.force_login(user)
    mock_get_create_export_plan.return_value = {
        'about_your_business': '', 'route_to_markets': {'route': 'test'}, 'marketing_approach': {'resources': 'xyz'}
    }
    response = client.get(reverse('exportplan:marketing-approach'), {'name': 'France', 'age_range': '30-34'})
    assert response.status_code == 200
    assert response.context_data['route_to_markets'] == '{"route": "test"}'
    assert response.context_data['route_choices']
    assert response.context_data['promotional_choices']


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
