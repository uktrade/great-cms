from unittest import mock
from django.http import HttpResponse

import pytest

from django.contrib.auth.models import AnonymousUser

from core import helpers, middleware
from tests.unit.core import factories
from tests.unit.exportplan.factories import ExportPlanPageFactory, ExportPlanPseudoDashboardPageFactory
from core.middleware import GADataMissingException


@pytest.fixture(autouse=True)
def mock_company_profile(mock_get_company_profile):
    mock_get_company_profile.return_value = {
        'expertise_products_services': {'other': ['Vodka']},
        'expertise_countries': [],
        'expertise_industries': [],
    }
    return mock_get_company_profile


@mock.patch.object(helpers, 'store_user_location')
def test_stores_user_location(mock_store_user_location, rf, user):
    request = rf.get('/')
    request.user = user

    middleware.UserLocationStoreMiddleware().process_request(request)

    assert mock_store_user_location.call_count == 1
    assert mock_store_user_location.call_args == mock.call(request)


@mock.patch.object(helpers, 'store_user_location')
def test_stores_user_location_anon_user(mock_store_user_location, rf):
    request = rf.get('/')
    request.user = AnonymousUser()

    middleware.UserLocationStoreMiddleware().process_request(request)

    assert mock_store_user_location.call_count == 0


@pytest.mark.django_db
def test_user_specific_redirect_middleware(domestic_site, client):
    learn_page = factories.LandingPageFactory(parent=domestic_site.root_page, slug='learn')
    introduction_page = factories.ListPageFactory(
        parent=learn_page, slug='introduction', template='learn/automated_list_page.html'
    )
    categories_page = factories.CuratedListPageFactory(parent=learn_page, slug='categories')
    # Given the user has gone to /learn/introduction/
    response = client.get(introduction_page.url)

    assert response.status_code == 200

    # When the user next goes to /learn/ or /learn/introduction/
    for page in [learn_page, introduction_page]:
        response = client.get(page.url)

        # Then they should be redirected to /learn/categories/
        assert response.status_code == 302
        assert response.url == categories_page.url


@pytest.mark.django_db
def test_user_specific_redirect_exportplan_middleware_logged_in_company_name_set(
    domestic_site, client, user, mock_get_company_profile, patch_export_plan
):
    exportplan_page = ExportPlanPageFactory(parent=domestic_site.root_page, slug='export-plan')
    exportplan_dashboard_page = ExportPlanPseudoDashboardPageFactory(parent=exportplan_page, slug='dashboard')

    # Given the user is logged in
    client.force_login(user)

    # And the compay name is set
    mock_get_company_profile.return_value = {'name': 'Example corp'}

    # When the user next goes to /export-plan/ or /export-plan/dasbboard/
    for page in [exportplan_page, exportplan_dashboard_page]:
        response = client.get(page.url)

        # Then they should not be redirected
        assert response.status_code == 200


@pytest.mark.django_db
def test_user_product_expertise_middleware(domestic_site, client, mock_update_company_profile, user):
    client.force_login(user)

    topic_page = factories.ListPageFactory(parent=domestic_site.root_page)
    lesson_page = factories.DetailPageFactory(parent=topic_page)

    response = client.get(
        lesson_page.url,
        {'product': ['Vodka', 'Potassium'], 'remember-expertise-products-services': True, 'hs_codes': [1, 2]}
    )
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        sso_session_id=user.session_id,
        data={
            'expertise_products_services': {'other': ['Vodka', 'Potassium']},
            'hs_codes': ['1', '2']
        }
    )


@pytest.mark.django_db
def test_user_product_expertise_middleware_no_company(
    domestic_site, client, mock_update_company_profile, user, mock_get_company_profile
):
    mock_get_company_profile.return_value = None
    client.force_login(user)

    topic_page = factories.ListPageFactory(parent=domestic_site.root_page)
    lesson_page = factories.DetailPageFactory(parent=topic_page)

    response = client.get(
        lesson_page.url,
        {'product': ['Vodka', 'Potassium'], 'remember-expertise-products-services': True, 'hs_codes': [1, 2]}
    )
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        sso_session_id=user.session_id,
        data={
            'expertise_products_services': {'other': ['Vodka', 'Potassium']},
            'hs_codes': ['1', '2']
        }
    )


@pytest.mark.skip(reason='All DetailPage templates require login. Reinstate for template that allows anon user')
def test_user_product_expertise_middleware_not_logged_in(domestic_site, client, mock_update_company_profile):
    topic_page = factories.ListPageFactory(parent=domestic_site.root_page)
    lesson_page = factories.DetailPageFactory(parent=topic_page)

    response = client.get(
        lesson_page.url,
        {'product': ['Vodka', 'Potassium'], 'remember-expertise-products-services': True}
    )

    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 0


@pytest.mark.django_db
def test_user_product_expertise_middleware_not_store(domestic_site, client, mock_update_company_profile, user):
    client.force_login(user)

    topic_page = factories.ListPageFactory(parent=domestic_site.root_page)
    lesson_page = factories.DetailPageFactory(parent=topic_page)

    response = client.get(
        lesson_page.url,
        {'product': ['Vodka', 'Potassium']}
    )
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 0


@pytest.mark.django_db
def test_user_product_expertise_middleware_not_store_idempotent(
    domestic_site, client, mock_update_company_profile, user
):
    client.force_login(user)

    topic_page = factories.ListPageFactory(parent=domestic_site.root_page)
    lesson_page = factories.DetailPageFactory(parent=topic_page)

    response = client.get(
        lesson_page.url,
        {'product': ['Vodka'], 'remember-expertise-products-services': True}
    )
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 0


def dummy_valid_ga_360_response():
    payload = {
        'page_id': 'TestPageId',
        'business_unit': 'Test App',
        'site_section': 'Test Section',
        'site_language': 'de',
        'user_id': '1234',
        'login_status': True
    }

    response = HttpResponse()
    response.status_code = 200
    response.context_data = {'ga360': payload}
    return response


def test_check_ga_360_tags_allows_valid_response():
    response = dummy_valid_ga_360_response()
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None


def test_check_ga_360_allows_redirects():
    response = HttpResponse()
    response.status_code = 301
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None


def test_check_ga_360_allows_responses_marked_as_skip_ga360():
    response = HttpResponse()
    response.status_code = 200
    response.skip_ga360 = True
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None


def test_check_ga_360_rejects_responses_missing_a_required_field():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360'] = {}
    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response({}, response)

    assert "'business_unit' is a required property" \
           in str(exception.value)


def test_check_ga_360_rejects_responses_where_a_required_field_is_null():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360']['business_unit'] = None
    instance = middleware.CheckGATags()

    with pytest.raises(GADataMissingException) as exception:
        instance.process_response({}, response)

    assert "None is not of type 'string'" in str(exception.value)


def test_check_ga_360_allows_null_values_for_nullable_fields():
    response = dummy_valid_ga_360_response()
    response.context_data['ga360']['user_id'] = None
    instance = middleware.CheckGATags()

    processed_response = instance.process_response({}, response)

    assert processed_response is not None
