from io import BytesIO
from unittest import mock
import pytest

from PIL import Image, ImageDraw
from requests.exceptions import HTTPError

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

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
        'target_markets_research': '',
        'adaptation_target_market': [],
        'target_market_documents': {'document_name': 'test'},
        'route_to_markets': {'route': 'test'},
        'marketing_approach': {'resources': 'xyz'},
        'company_objectives': {},
        'export_countries': [{'country_name': 'Netherlands', 'country_iso2_code': 'NL'}]
    }


@pytest.fixture(autouse=True)
def mock_get_create_export_plan(export_plan_data):
    patch = mock.patch.object(
        helpers,
        'get_or_create_export_plan',
        return_value=export_plan_data
    )

    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_cia_factbook_data():
    patch = mock.patch.object(
        helpers,
        'get_cia_world_factbook_data',
        return_value={'language': 'Dutch', 'note': 'Many other too'}
    )

    yield patch.start()
    patch.stop()


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
@mock.patch.object(helpers, 'get_all_lesson_details', return_value={})
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_sections(
        mock_get_create_exportplan, mock_get_all_lessons, export_plan_data, slug, client, user
):
    mock_get_create_exportplan.return_value = export_plan_data
    client.force_login(user)
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_exportplan_section_marketing_approach(client, user):
    client.force_login(user)
    response = client.get(reverse('exportplan:marketing-approach'), {'name': 'France', 'age_range': '30-34'})
    assert response.status_code == 200
    assert response.context_data['route_to_markets'] == '{"route": "test"}'
    assert response.context_data['route_choices']
    assert response.context_data['promotional_choices']


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
@mock.patch.object(helpers, 'get_cia_world_factbook_data')
def test_adaption_for_target_markets_context(mock_get_factbook_data, client, user):
    client.force_login(user)

    mock_get_factbook_data.return_value = {'language': 'Dutch', 'note': 'Many other too'}
    slug = slugify('Adaptation for your target market')
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200

    assert mock_get_factbook_data.call_count == 1
    assert mock_get_factbook_data.call_args == mock.call(country='Netherlands', key='people,languages')

    response.context_data['languages'] = {'language': 'Dutch', 'note': 'Many other too'}
    response.context_data['check_duties_link'] = 'https://www.check-duties-customs-exporting-goods.service.gov.uk/'
    response.context_data['target_market_documents'] = {'document_name': 'test'}


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_all_lesson_details')
def test_about_your_business_has_lessons(mock_get_all_lesson_details, client, user):
    client.force_login(user)

    mock_get_all_lesson_details.return_value = {
        'lesson1': {'title': 'my lesson', 'url': 'my url'}
    }
    slug = slugify('About your business')
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200

    assert mock_get_all_lesson_details.call_count == 1

    assert response.context_data['lesson_details'] == {'lesson1': {'title': 'my lesson', 'url': 'my url'}}


@pytest.mark.django_db
@pytest.mark.parametrize('slug', set(data.SECTION_SLUGS))
def test_export_plan_mixin(export_plan_data, slug, client, user):
    client.force_login(user)
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200

    if not slug == data.SECTION_SLUGS[-1]:
        assert response.context_data['next_section'] == {
            'title': data.SECTION_TITLES[data.SECTION_SLUGS.index(slug) + 1],
            'url': data.SECTION_URLS[data.SECTION_SLUGS.index(slug) + 1],
        }

    assert response.context_data['current_section'] == {
        'title': data.SECTION_TITLES[data.SECTION_SLUGS.index(slug)],
        'url': data.SECTION_URLS[data.SECTION_SLUGS.index(slug)],
    }
    assert response.context_data['sections'] == data.SECTION_TITLES_URLS
    assert response.context_data['export_plan'] == export_plan_data
