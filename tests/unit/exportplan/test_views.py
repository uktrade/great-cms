from io import BytesIO
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image, ImageDraw
from requests.exceptions import HTTPError

from config import settings
from directory_api_client.client import api_client
from exportplan import data, helpers
from tests.helpers import create_response, reload_urlconf
from tests.unit.exportplan.factories import ExportPlanDashboardPageFactory


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
        'modified': '2019-04-05T06:43:23.00000Z',
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
        'objectives': {'rationale': 'business rationale'},
        'export_countries': [{'country_name': 'Netherlands', 'country_iso2_code': 'NL'}],
    }


@pytest.fixture()
def export_plan_data_with_no_countries():
    return {
        'about_your_business': '',
        'target_markets_research': '',
        'adaptation_target_market': [],
        'target_market_documents': {'document_name': 'test'},
        'route_to_markets': {'route': 'test'},
        'marketing_approach': {'resources': 'xyz'},
        'company_objectives': {},
        'objectives': {'rationale': 'business rationale'},
        'export_countries': [],
    }


@pytest.fixture(autouse=True)
def mock_get_create_export_plan(export_plan_data):
    patch = mock.patch.object(helpers, 'get_or_create_export_plan', return_value=export_plan_data)

    yield patch.start()
    patch.stop()


@pytest.fixture()
def mock_get_create_export_plan_with_no_countries(export_plan_data_with_no_countries):
    patch = mock.patch.object(helpers, 'get_or_create_export_plan', return_value=export_plan_data_with_no_countries)

    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_cia_factbook_data():
    patch = mock.patch.object(
        helpers, 'get_cia_world_factbook_data', return_value={'language': 'Dutch', 'note': 'Many other too'}
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
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_export_plan_builder_landing_page(
    mock_get_create_export_plan,
    client,
    exportplan_dashboard,
    user,
    mock_get_company_profile,
    company_profile_data,
    export_plan_data,
):
    mock_get_create_export_plan.return_value = export_plan_data
    mock_get_company_profile.return_value = company_profile_data

    client.force_login(user)

    response = client.get('/export-plan/dashboard/')
    assert response.status_code == 200
    assert response.context['sections'] == data.SECTION_TITLES


@pytest.mark.django_db
@pytest.mark.parametrize('slug', set(data.SECTIONS.keys()) - {'marketing-approach', 'objectives'})
@mock.patch.object(helpers, 'get_all_lesson_details', return_value={})
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_sections(mock_get_create_exportplan, mock_get_all_lessons, export_plan_data, slug, client, user):
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
    assert mock_update_company.call_args == mock.call(sso_session_id=user.session_id, data={'logo': mock.ANY})


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

    mock_get_all_lesson_details.return_value = {'lesson1': {'title': 'my lesson', 'url': 'my url'}}
    slug = slugify('About your business')
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200

    assert mock_get_all_lesson_details.call_count == 1

    assert response.context_data['lesson_details'] == {'lesson1': {'title': 'my lesson', 'url': 'my url'}}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'slug, next_slug',
    (
        ('about-your-business', 'business-objectives'),
        ('business-objectives', 'target-markets-research'),
        ('target-markets-research', 'adaptation-for-your-target-market'),
        ('adaptation-for-your-target-market', 'marketing-approach'),
        ('marketing-approach', 'costs-and-pricing'),
        ('costs-and-pricing', 'finance'),
        ('finance', 'payment-methods'),
        ('payment-methods', 'travel-and-business-policies'),
        ('travel-and-business-policies', 'business-risk'),
        ('business-risk', None),
    ),
)
def test_export_plan_mixin(export_plan_data, slug, next_slug, client, user):
    client.force_login(user)

    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200
    assert response.context_data['next_section'] == data.SECTIONS.get(next_slug)
    assert response.context_data['current_section'] == data.SECTIONS[slug]
    assert response.context_data['sections'] == data.SECTION_URLS
    assert response.context_data['export_plan'] == export_plan_data


@pytest.mark.django_db
def test_404_when_invalid_section_slug(client, user):
    url = reverse('exportplan:section', kwargs={'slug': 'foo'})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_url_with_export_plan_country_selected(mock_get_create_export_plan_with_no_countries, client, user):
    url = reverse('exportplan:target-markets-research')
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_redirect_to_service_page_for_disabled_urls(client, user):
    settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED = True
    reload_urlconf('exportplan.data')
    slug = slugify(data.SECTIONS_DISABLED[0])
    url = reverse('exportplan:section', kwargs={'slug': slug})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('exportplan:service-page')


@pytest.mark.django_db
def test_disabled_urls_feature_flag_disabled(client, user):
    settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED = False
    reload_urlconf('exportplan.data')

    assert len(data.SECTIONS_DISABLED) == 0
    slug = slugify(data.SECTION_TITLES[0])
    url = reverse('exportplan:section', kwargs={'slug': slug})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_service_page_context(client, user):
    client.force_login(user)
    url = reverse('exportplan:service-page')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['sections'] == list(data.SECTIONS.values())


@pytest.mark.django_db
def test_exportplan_dashboard(
    client,
    user,
    domestic_homepage,
    get_request,
    patch_set_user_page_view,
):
    client.force_login(user)
    dashboard = ExportPlanDashboardPageFactory(parent=domestic_homepage, slug='dashboard')
    context_data = dashboard.get_context(get_request)
    assert context_data.get('export_plan').get('id') == 1
    assert len(context_data.get('sections')) == 10
    assert context_data.get('sections')[0].get('url') == '/export-plan/section/about-your-business/'
