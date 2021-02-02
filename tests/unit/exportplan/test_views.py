import json
from collections import OrderedDict
from io import BytesIO
from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.text import slugify
from freezegun import freeze_time
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
    assert response.context['sections'][0] == {
        'title': 'About your business',
        'url': '/export-plan/section/about-your-business/',
        'disabled': False,
        'lessons': ['move-accidental-exporting-strategic-exporting'],
        'is_complete': False,
    }


@pytest.mark.django_db
@pytest.mark.parametrize('slug', set(data.SECTIONS.keys()) - {'marketing-approach', 'objectives'})
@mock.patch.object(helpers, 'get_lesson_details', return_value={})
@mock.patch.object(helpers, 'get_or_create_export_plan')
def test_exportplan_sections(mock_get_create_exportplan, mock_get_lessons, export_plan_data, slug, client, user):
    mock_get_create_exportplan.return_value = export_plan_data
    client.force_login(user)
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_exportplan_section_marketing_approach(mock_get_country_data, mock_get_cia_world_factbook_data, client, user):
    client.force_login(user)
    response = client.get(reverse('exportplan:marketing-approach'), {'name': 'France', 'age_range': '30-34'})
    assert response.status_code == 200
    assert response.context_data['route_to_markets'] == '{"route": "test"}'
    assert response.context_data['route_choices']
    assert response.context_data['promotional_choices']
    assert response.context_data['target_age_group_choices']
    assert response.context_data['demographic_data'] == {
        **mock_get_country_data.return_value,
        **mock_get_cia_world_factbook_data.return_value,
    }
    assert response.context_data['selected_age_groups'] == '["25-29", "47-49"]'


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
@mock.patch.object(helpers, 'get_lesson_details')
def test_about_your_business_has_lessons(mock_get_lesson_details, client, user):
    client.force_login(user)

    slug = slugify('About your business')
    lessons = data.SECTIONS[slug]['lessons']
    mock_get_lesson_details.return_value = {lessons[0]: {'title': 'my lesson', 'url': 'my url'}}
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert response.status_code == 200

    assert mock_get_lesson_details.call_count == 1
    assert mock_get_lesson_details.call_args == mock.call(lessons)

    assert response.context_data['lesson_details'] == {lessons[0]: {'title': 'my lesson', 'url': 'my url'}}


@freeze_time('2012-01-14 03:21:34')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'slug, next_slug',
    (
        ('about-your-business', 'business-objectives'),
        ('business-objectives', 'target-markets-research'),
        ('target-markets-research', 'adaptation-for-your-target-market'),
        ('adaptation-for-your-target-market', 'marketing-approach'),
        ('marketing-approach', 'costs-and-pricing'),
        ('costs-and-pricing', 'funding-and-credit'),
        ('funding-and-credit', 'getting-paid'),
        ('getting-paid', 'travel-and-business-policies'),
        ('travel-and-business-policies', 'business-risk'),
        ('business-risk', None),
    ),
)
def test_export_plan_mixin(export_plan_data, slug, next_slug, mock_update_export_plan_client, client, user):
    client.force_login(user)
    response = client.get(reverse('exportplan:section', kwargs={'slug': slug}))

    assert mock_update_export_plan_client.call_count == 1
    assert mock_update_export_plan_client.call_args == mock.call(
        data={'ui_progress': {slug: OrderedDict([('date_last_visited', '2012-01-14T03:21:34+00:00')])}},
        id=1,
        sso_session_id='123',
    )
    assert response.status_code == 200
    assert response.context_data['next_section'] == data.SECTIONS.get(next_slug)
    assert response.context_data['current_section'] == data.SECTIONS[slug]
    assert response.context_data['sections'][0] == {
        'title': 'About your business',
        'url': '/export-plan/section/about-your-business/',
        'disabled': False,
        'lessons': ['move-accidental-exporting-strategic-exporting'],
        'is_complete': True,
    }
    assert response.context_data['export_plan'] == export_plan_data
    assert response.context_data['export_plan_progress'] == {
        'export_plan_progress': {'sections_total': 10, 'sections_completed': 1, 'percentage_completed': 0.1}
    }


@pytest.mark.django_db
def test_404_when_invalid_section_slug(client, user):
    url = reverse('exportplan:section', kwargs={'slug': 'foo'})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_url_with_export_plan_country_selected(mock_get_comtrade_data, mock_get_create_export_plan, client, user):
    # Remove countries selection
    mock_get_create_export_plan.return_value.update({'export_countries': None})
    url = reverse('exportplan:target-markets-research')
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assert mock_get_comtrade_data.call_count == 0


@pytest.mark.django_db
def test_target_markets_research(mock_get_comtrade_data, client, user):
    url = reverse('exportplan:target-markets-research')
    client.force_login(user)

    response = client.get(url)

    assert response.context_data['target_age_group_choices']
    assert response.context_data['insight_data'] == json.dumps(mock_get_comtrade_data.return_value)
    assert response.context_data['selected_age_groups'] == '["35-40"]'
    assert response.status_code == 200
    assert mock_get_comtrade_data.call_count == 1

    assert mock_get_comtrade_data.call_args == mock.call(commodity_code='220850', countries_list=['Netherlands'])


@pytest.mark.django_db
def test_cost_and_pricing(cost_pricing_data, client, user):
    url = reverse('exportplan:costs-and-pricing')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert (
        response.context_data['check_duties_link'] == 'https://www.check-duties-customs-exporting-goods.service.gov.uk/'
    )
    assert response.context_data['export_unit_choices'][0] == {'label': 'metre(s)', 'value': 'm'}
    assert response.context_data['export_timeframe_choices'][0] == {'label': 'day(s)', 'value': 'd'}
    assert response.context_data['currency_choices'][0] == {'label': 'EUR', 'value': 'eur'}
    assert response.context_data['costs_and_pricing_data'] == json.dumps(
        {
            'direct_costs': {'product_costs': '10.00', 'labour_costs': '5.00', 'other_direct_costs': ''},
            'overhead_costs': {
                'product_adaption': '',
                'freight_logistics': '',
                'agent_distributor_fees': '',
                'marketing': '1345.00',
                'insurance': '10.00',
                'other_overhead_costs': '',
            },
            'total_cost_and_price': {
                'units_to_export_first_period': {'unit': '', 'value': 22},
                'units_to_export_second_period': {'unit': '', 'value': ''},
                'final_cost_per_unit': '16.00',
                'average_price_per_unit': '',
                'net_price': '22.00',
                'local_tax_charges': '5.23',
                'duty_per_unit': '15.13',
                'gross_price_per_unit_invoicing_currency': {'unit': '', 'value': ''},
            },
        }
    )
    assert response.context_data['calculated_pricing'] == json.dumps(
        {
            'calculated_cost_pricing': {
                'total_direct_costs': '15.00',
                'total_overhead_costs': '1355.00',
                'profit_per_unit': '6.00',
                'potential_total_profit': '132.00',
                'gross_price_per_unit': '42.36',
                'total_export_costs': '1685.00',
                'estimated_costs_per_unit': '76.59',
            }
        }
    )


@pytest.mark.django_db
def test_getting_paid(export_plan_data, client, user):
    url = reverse('exportplan:getting-paid')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['payment_method_choices'][0] == {
        'label': 'International bank transfers',
        'value': 'INTERNATIONAL_BANK_TRANSFER',
    }
    assert response.context_data['payment_term_choices'][0] == {
        'label': 'Payment in advance',
        'value': 'PAYMENT_IN_ADVANCE',
    }
    assert response.context_data['transport_choices']['All forms of transport'][0] == {
        'label': 'Ex Works (EXW)',
        'value': 'EX_WORKS',
    }
    assert response.context_data['transport_choices']['Water transport'][0] == {
        'label': 'Free Alongside Ship (FAS)',
        'value': 'FREE_ALONG_SHIP',
    }
    assert response.context_data['getting_paid_data'] == json.dumps(export_plan_data['getting_paid'])


@pytest.mark.django_db
def test_funding_and_credit(export_plan_data, client, user):
    url = reverse('exportplan:funding-and-credit')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200

    assert response.context_data['funding_options'][0] == {'label': 'Bank loan', 'value': 'BANK_LOAN'}
    assert response.context_data['funding_and_credit'] == export_plan_data['funding_and_credit']
    assert response.context_data['estimated_costs_per_unit'] == '76.59'
    assert response.context_data['funding_credit_options'] == json.dumps(export_plan_data['funding_credit_options'])


@pytest.mark.django_db
def test_redirect_to_service_page_for_disabled_urls(client, user):
    settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST = ['Costs and pricing', 'About your business']
    reload_urlconf('exportplan.data')
    slug = slugify(data.SECTIONS_DISABLED[0])
    url = reverse('exportplan:section', kwargs={'slug': slug})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('exportplan:service-page')


@pytest.mark.django_db
def test_disabled_urls_feature_flag_disabled(client, user):
    settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST = []
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
    assert response.context['sections'][0] == {
        'title': 'About your business',
        'url': '/export-plan/section/about-your-business/',
        'disabled': False,
        'lessons': ['move-accidental-exporting-strategic-exporting'],
        'is_complete': True,
    }


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
    assert context_data['export_plan_progress'] == {
            'export_plan_progress': {'sections_total': 10, 'sections_completed': 0, 'percentage_completed': 0}
        }
