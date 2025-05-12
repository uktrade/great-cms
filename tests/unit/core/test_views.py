import json
import re
from unittest import mock
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urlencode

import pytest
from directory_forms_api_client import actions
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import JsonResponse
from django.http.cookie import SimpleCookie
from django.test import Client, TestCase, modify_settings, override_settings
from django.urls import reverse, reverse_lazy
from formtools.wizard.views import normalize_name
from pytest_django.asserts import assertTemplateUsed
from rest_framework import status
from wagtail.images.views.chooser import (
    ChosenResponseMixin,
    CreateViewMixin,
    ImageUploadViewMixin,
    SelectFormatResponseMixin,
)
from wagtail.models import Locale, Site

from core import cms_slugs, forms, helpers, serializers, views
from core.models import HCSAT
from core.pingdom.services import DatabaseHealthCheck
from directory_api_client import api_client
from directory_sso_api_client import sso_api_client
from domestic.views.campaign import CampaignView
from tests.helpers import create_response, make_test_video
from tests.unit.core.factories import (
    CuratedListPageFactory,
    DetailPageFactory,
    LessonPlaceholderPageFactory,
    ListPageFactory,
    MicrositeFactory,
    MicrositePageFactory,
    TopicPageFactory,
)
from tests.unit.domestic.factories import (
    ArticleListingPageFactory,
    ArticlePageFactory,
    DomesticDashboardFactory,
    TopicLandingPageFactory,
)
from tests.unit.learn.factories import LessonPageFactory

BETA_AUTH_TOKEN_PAST = (
    'gAAAAABfCpH53lJcM0TiiXTqD7X18yRoZHOjy-rbSogRxB0v011FMb6rCkMeizffou-z80D9DPL1PWRA7sn9NBrUS'
    '-M7FTQeapvntabhj-on62OFlNvzVMQ= '
)


def submit_step_factory(client, url_name, view_class):
    step_names = iter([name for name, form in view_class.form_list])
    view_name = normalize_name(view_class.__name__)

    def submit_step(data, step_name=None, params={}):
        step_name = step_name or next(step_names)
        path = reverse(url_name, kwargs={'step': step_name})
        return client.post(
            path=f'{path}?{urlencode(params, doseq=True)}',
            data={
                view_name + '-current_step': step_name,
                **{step_name + '-' + key: value for key, value in data.items()},
            },
        )

    return submit_step


@pytest.fixture
def submit_signup_tailored_content_wizard_step(client):
    return submit_step_factory(
        client=client,
        url_name='core:signup-wizard-tailored-content',
        view_class=views.SignupForTailoredContentWizardView,
    )


@pytest.fixture
def submit_signup_export_plan_wizard_step(client):
    return submit_step_factory(
        client=client,
        url_name='core:signup-wizard-export-plan',
        view_class=views.SignupForExportPlanWizardView,
    )


@pytest.fixture
def company_data():
    return {
        'expertise_industries': json.dumps(['Science']),
        'expertise_countries': json.dumps(['USA']),
    }


@pytest.fixture
def contact_form_data(captcha_stub):
    return {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'comment': 'Help please',
        'g-recaptcha-response': captcha_stub,
        'terms_agreed': True,
    }


@pytest.mark.django_db
def test_service_removed_page(
    client,
    domestic_homepage,
    domestic_site,
):
    # get a path we know will trigger the service-removed view
    response = client.get('/triage/foo/')
    assert response.status_code == 200

    response = client.get('/triage/')
    assert response.status_code == 200

    response = client.get('/custom/')
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_company_profile')
def test_api_update_company_success(mock_update_company_profile, mock_get_company_profile, client, user, company_data):
    mock_update_company_profile.return_value = create_response()
    mock_get_company_profile.return_value = {'foo': 'bar'}
    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)
    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        data={
            'expertise_industries': ['Science'],
            'expertise_countries': ['USA'],
        },
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
def test_api_update_company_too_many_companies(client, user):
    company_data = {
        'expertise_countries': json.dumps(['USA', 'China', 'Australia', 'New Zealand']),
    }

    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 400
    assert response.json() == {
        'expertise_countries': [serializers.CompanySerializer.MESSAGE_TOO_MANY_COUNTRIES],
    }


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_company_profile')
def test_api_update_company_no_name(mock_update_company_profile, mock_get_company_profile, client, user, company_data):
    mock_update_company_profile.return_value = create_response()
    mock_get_company_profile.return_value = {}
    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 200
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        data={
            'name': 'unnamed sso-1 company',
            'expertise_industries': ['Science'],
            'expertise_countries': ['USA'],
        },
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
def test_api_update_company_not_logged_in(client, company_data):
    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
@mock.patch.object(api_client.personalisation, 'events_by_location_list')
@mock.patch.object(api_client.personalisation, 'export_opportunities_by_relevance_list')
@mock.patch.object(sso_api_client.user, 'get_user_lesson_completed')
def test_dashboard_page_logged_in(
    mock_get_user_lesson_completed,
    mock_events_by_location_list,
    mock_export_opportunities_by_relevance_list,
    patch_set_user_page_view,
    patch_get_user_page_views,
    mock_get_company_profile,
    domestic_homepage,
    domestic_dashboard,
    client,
    user,
    mock_get_user_profile,
):
    mock_get_user_lesson_completed.return_value = create_response(json_body={'results': []})
    mock_events_by_location_list.return_value = create_response(json_body={'results': []})
    mock_export_opportunities_by_relevance_list.return_value = create_response(json_body={'results': []})
    client.force_login(user)
    response = client.get(cms_slugs.DASHBOARD_URL)
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_page_not_logged_in(domestic_homepage, domestic_dashboard, client, user):
    response = client.get(cms_slugs.DASHBOARD_URL)
    assert response.status_code == 302
    assert response.url == cms_slugs.SIGNUP_URL + '?next=/dashboard/'


@pytest.mark.django_db
@mock.patch.object(api_client.personalisation, 'events_by_location_list')
@mock.patch.object(api_client.personalisation, 'export_opportunities_by_relevance_list')
@mock.patch.object(sso_api_client.user, 'get_user_lesson_completed')
def test_dashboard_page_lesson_progress(
    mock_get_user_lesson_completed,
    mock_export_opportunities_by_relevance_list,
    mock_events_by_location_list,
    patch_set_user_page_view,
    patch_get_user_page_views,
    mock_export_plan_detail_list,
    mock_get_company_profile,
    client,
    user,
    get_request,
    domestic_homepage,
    domestic_site,
    mock_get_user_profile,
):
    mock_events_by_location_list.return_value = create_response(json_body={'results': []})
    mock_export_opportunities_by_relevance_list.return_value = create_response(json_body={'results': []})
    client.force_login(user)

    # given the user has read some lessons
    section_one = ListPageFactory(parent=domestic_homepage, slug='section-one', record_read_progress=True)
    section_two = ListPageFactory(parent=domestic_homepage, slug='section-two', record_read_progress=True)

    module_one = CuratedListPageFactory(parent=section_one, slug='section-one-module-one')
    module_two = CuratedListPageFactory(parent=section_two, slug='section-two-module-one')
    CuratedListPageFactory(parent=section_two, slug='section-two-module-two')

    topic_1_1 = TopicPageFactory(parent=module_one, title='Module one, first topic block')
    topic_1_2 = TopicPageFactory(parent=module_one, title='Module one, second topic block')

    topic_2_1 = TopicPageFactory(parent=module_two, title='Module two, first topic block')
    topic_2_2 = TopicPageFactory(parent=module_two, title='Module two, second topic block')

    # Section 1 Module 1 Topic 1 gets two children
    lesson_one = DetailPageFactory(
        parent=topic_1_1,
        slug='lesson-one',
    )
    LessonPlaceholderPageFactory(
        title='Placeholder To Show They Do Not Interfere With Counts',
        parent=topic_1_1,
    )

    # Section 1 Module 1 Topic 2 gets one child
    lesson_two = DetailPageFactory(
        parent=topic_1_2,
        slug='lesson-two',
    )

    # Section 1 Module 2 Topic 1 gets two children
    DetailPageFactory(
        parent=topic_2_1,
        slug='lesson-three',
    )
    DetailPageFactory(
        parent=topic_2_1,  # ie, in same topic block as one above
        slug='lesson-four',
    )

    # Section 1 Module 2 Topic 2 children
    LessonPlaceholderPageFactory(
        title='Another Placeholder To Show They Do Not Interfere With Counts',
        parent=topic_2_2,
    )
    lesson_five = DetailPageFactory(
        parent=topic_2_2,  # correct
        slug='lesson-five',
    )

    # create dashboard
    dashboard = DomesticDashboardFactory(parent=domestic_homepage, slug='dashboard')

    mock_get_user_lesson_completed.return_value = create_response(
        json_body={
            'result': 'ok',
            'lesson_completed': [
                {'lesson': lesson_one.id},
                {'lesson': lesson_two.id},
            ],
        }
    )

    context_data = dashboard.get_context(get_request)
    # check the progress
    assert len(context_data['module_pages']) == 2
    assert context_data['module_pages'][0]['page'].id == module_one.id
    assert context_data['module_pages'][1]['page'].id == module_two.id
    assert context_data['module_pages'][0]['total_pages'] == 2
    assert context_data['module_pages'][1]['total_pages'] == 3
    assert context_data['module_pages'][0]['completion_count'] == 2
    assert context_data['module_pages'][0]['completed_lesson_pages'] == {
        topic_1_1.id: set([lesson_one.id]),
        topic_1_2.id: set([lesson_two.id]),
    }
    assert context_data['module_pages'][1]['completion_count'] == 0
    assert context_data['module_pages'][1]['completed_lesson_pages'] == {}

    mock_get_user_lesson_completed.return_value = create_response(
        json_body={
            'result': 'ok',
            'lesson_completed': [{'lesson': lesson_one.id}, {'lesson': lesson_two.id}, {'lesson': lesson_five.id}],
        }
    )

    context_data = dashboard.get_context(get_request)
    # WARNING! The topics should swap round as two is in progress
    # and has more unread than one
    assert context_data['module_pages'][0]['page'].id == module_two.id
    assert context_data['module_pages'][1]['page'].id == module_one.id
    assert context_data['module_pages'][0]['completion_count'] == 1
    assert context_data['module_pages'][0]['completed_lesson_pages'] == {
        topic_2_2.id: set([lesson_five.id]),
    }
    assert context_data['module_pages'][1]['completion_count'] == 2
    assert context_data['module_pages'][1]['completed_lesson_pages'] == {
        topic_1_1.id: set([lesson_one.id]),
        topic_1_2.id: set([lesson_two.id]),
    }


@pytest.mark.django_db
def test_dashboard_apis_ok(
    client,
    user,
    get_request,
    patch_get_dashboard_export_opportunities,
    patch_set_user_page_view,
    patch_get_user_page_views,
    patch_get_user_lesson_completed,
    domestic_homepage,
    mock_get_user_profile,
):
    patch_get_dashboard_export_opportunities.stop()

    with patch('directory_api_client.api_client.personalisation.events_by_location_list') as events_api_results:
        events_api_results.return_value = Mock(
            status_code=200,
            **{
                'json.return_value': {
                    'results': [
                        {
                            'name': 'Global Aid and Development Directory',
                            'content': (
                                'DIT is producing a directory of companies '
                                'who supply, or would like to supply, relevant humanitarian aid '
                                'and development products and services to the United Nations '
                                'family of organisations and NGOs.  '
                            ),
                            'location': {'city': 'London'},
                            'url': 'www.example.com',
                            'date': '2020-06-06',
                        },
                        {
                            'name': 'Less Info',
                            'content': 'Content',
                            'url': 'www.example.com',
                        },
                    ]
                }
            },
        )

        with patch(
            'directory_api_client.api_client.personalisation.export_opportunities_by_relevance_list'
        ) as exops_api_results:
            exops_api_results.return_value = Mock(
                status_code=200,
                **{
                    'json.return_value': {
                        'results': [
                            {
                                'title': 'French sardines required',
                                'url': (
                                    'http://exops.trade.great:3001/export-opportunities/'
                                    'opportunities/french-sardines-required'
                                ),
                                'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
                                'published_date': '2020-01-14T15:26:45.334Z',
                                'closing_date': '2020-06-06',
                                'source': 'post',
                            }
                        ]
                    }
                },
            )

            client.force_login(user)

            dashboard = DomesticDashboardFactory(parent=domestic_homepage, slug='dashboard')
            context_data = dashboard.get_context(get_request)

            assert context_data['export_opportunities'] == [
                {
                    'title': 'French sardines required',
                    'description': 'Nam dolor nostrum distinctio.…',
                    'source': 'post',
                    'url': 'http://exops.trade.great:3001/export-opportunities/opportunities/french-sardines-required',
                    'published_date': '14 Jan 2020',
                    'closing_date': '06 Jun 2020',
                }
            ]


@pytest.mark.django_db
def test_dashboard_apis_fail(
    client,
    user,
    get_request,
    patch_get_dashboard_export_opportunities,
    patch_set_user_page_view,
    patch_get_user_page_views,
    patch_get_user_lesson_completed,
    domestic_homepage,
    mock_get_user_profile,
):
    patch_get_dashboard_export_opportunities.stop()
    patch_get_user_lesson_completed.stop()
    with patch('directory_api_client.api_client.personalisation.events_by_location_list') as events_api_results:
        events_api_results.return_value = Mock(status_code=500, **{'json.return_value': {}})

        with patch(
            'directory_api_client.api_client.personalisation.export_opportunities_by_relevance_list'
        ) as exops_api_results:
            exops_api_results.return_value = Mock(status_code=500, **{'json.return_value': {}})

            client.force_login(user)
            dashboard = DomesticDashboardFactory(parent=domestic_homepage, slug='dashboard')
            context_data = dashboard.get_context(get_request)

            assert context_data['export_opportunities'] == []


@pytest.mark.django_db
def test_capability_article_logged_in(client, user, mock_get_user_profile):
    client.force_login(user)
    url = reverse(
        'core:capability-article', kwargs={'topic': 'some topic', 'chapter': 'some chapter', 'article': 'some article'}
    )

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['topic_name'] == 'some topic'
    assert response.context_data['chapter_name'] == 'some chapter'
    assert response.context_data['article_name'] == 'some article'


@pytest.mark.django_db
def test_capability_article_not_logged_in(client):
    url = reverse(
        'core:capability-article', kwargs={'topic': 'some-topic', 'chapter': 'some-chapter', 'article': 'some-article'}
    )

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == f'{cms_slugs.SIGNUP_URL}?next={url}'


@pytest.mark.django_db
def test_login_page_not_logged_in(client):
    url = reverse('core:login')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_logged_in(client, user):
    client.force_login(user)
    url = reverse('core:login')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == cms_slugs.DASHBOARD_URL


@pytest.mark.django_db
def test_logout_not_logged_in(client):
    url = reverse('core:logout')

    response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_logout_logged_in_no_next_param(client, user, requests_mock):
    client.force_login(user)
    requests_mock.post(settings.SSO_PROXY_LOGOUT_URL, status_code=302)
    url = reverse('core:logout')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == settings.BASE_URL


@pytest.mark.django_db
def test_logout_logged_in_next_param(client, user, requests_mock):
    client.force_login(user)
    requests_mock.post(settings.SSO_PROXY_LOGOUT_URL, status_code=302)
    next_url = 'http://example.com/example'
    url = reverse('core:logout') + '?next=' + next_url

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == next_url


@pytest.mark.django_db
@mock.patch.object(helpers, 'search_commodity_by_term')
def test_search_commodity_by_term(mock_search_commodity_by_term, client):
    mock_search_commodity_by_term.return_value = data = [
        {'value': '123323', 'label': 'some description'},
        {'value': '223323', 'label': 'some other description'},
    ]
    term = 'some term'

    response = client.post(reverse('core:api-lookup-product'), {'proddesc': term})

    assert response.status_code == 200
    assert response.json() == data
    assert mock_search_commodity_by_term.call_count == 1
    assert mock_search_commodity_by_term.call_args == mock.call(term=term)


@pytest.mark.django_db
@mock.patch.object(helpers, 'search_commodity_refine')
def test_refine_commodity(mock_search_commodity_refine, client):
    mock_search_commodity_refine.return_value = data = [
        {'value': '123323', 'label': 'some description'},
        {'value': '223323', 'label': 'some other description'},
    ]

    response = client.post(
        reverse('core:api-lookup-product'),
        {'interaction_id': 1234, 'tx_id': 1234, 'value_id': 1234, 'value_string': 'processed'},
    )

    assert response.status_code == 200
    assert response.json() == data
    assert mock_search_commodity_refine.call_count == 1


@pytest.mark.django_db
@mock.patch.object(helpers, 'ccce_import_schedule')
def test_commodity_schedule(mock_ccce_import_schedule, client):
    mock_ccce_import_schedule.return_value = data = [
        {'value': '123323', 'label': 'some description'},
        {'value': '223323', 'label': 'some other description'},
    ]
    hs_code = '123456'

    response = client.get(reverse('core:api-lookup-product-schedule'), {'hs_code': hs_code})

    assert response.status_code == 200
    assert response.json() == data
    assert mock_ccce_import_schedule.call_count == 1
    assert mock_ccce_import_schedule.call_args == mock.call(hs_code=hs_code)


@pytest.mark.django_db
def test_get_countries(client):
    response = client.get(reverse('core:api-countries'))
    countries = response.json()
    assert response.status_code == 200
    assert len(countries) > 190
    assert 'id' in countries[0]
    assert 'name' in countries[0]
    assert 'region' in countries[0]


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_suggested_countries_by_hs_code')
def test_get_suggested_countries(mock_get_suggested_countries_by_hs_code, client, user):
    data = [
        {'hs_code': 4, 'country_name': 'Sweden', 'country_iso2': 'SE', 'region': 'Europe'},
        {'hs_code': 4, 'country_name': 'Spain', 'country_iso2': 'ES', 'region': 'Europe'},
    ]
    mock_get_suggested_countries_by_hs_code.return_value = data

    client.force_login(user)
    response = client.get(reverse('core:api-suggested-countries'), data={'hs_code': '20'})
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.django_db
def test_list_page_uses_right_template(domestic_homepage, rf, user, get_response):
    request = rf.get('/')
    request.user = user
    middleware = SessionMiddleware(get_response)
    middleware.process_request(request)
    request.session.save()
    topic_page = CuratedListPageFactory(parent=domestic_homepage)
    lesson_page = LessonPageFactory(parent=topic_page)
    response = lesson_page.serve(request)
    assert response.template_name == 'learn/detail_page.html'


@pytest.mark.parametrize(
    'test_url,template_name',
    (
        ('/hey-kid-do-a-kickflip/', 'core/404.html'),
        ('/international/expand-your-business-in-the-uk/hey-kid-do-a-kickflip/', 'international/404.html'),
        ('/international/hey-kid-do-a-kickflip/', 'international/404.html'),
    ),
)
@pytest.mark.django_db
def test_handler404(client, settings, test_url, template_name):
    response = client.get(test_url)
    assert response.template_name == template_name
    assert response.status_code == 404


@pytest.fixture
def signup_wizard_steps_data():
    return {
        views.STEP_START: {},
        views.STEP_WHAT_SELLING: {'choice': forms.WhatAreYouSellingForm.PRODUCTS},
        views.STEP_PRODUCT_SEARCH: {'products': 'Sharks,Crayons'},
        views.STEP_SIGN_UP: {},
    }


@pytest.mark.django_db
def test_signup_wizard_for_tailored_content_success(
    submit_signup_tailored_content_wizard_step, signup_wizard_steps_data, client
):
    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_START])
    assert response.status_code == 302

    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_WHAT_SELLING])
    assert response.status_code == 302

    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_PRODUCT_SEARCH])
    assert response.status_code == 302

    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_SIGN_UP])
    assert response.status_code == 302

    # note that the react component handles the logging in, so no need to submit the last step here,
    with pytest.raises(NotImplementedError):
        client.get(response.url)


@pytest.mark.django_db
def test_signup_wizard_for_tailored_content_step_labels_exposed(client):
    response = client.get(reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START}))
    assert response.context_data['step_labels'] == views.SignupForTailoredContentWizardView.step_labels

    response = client.get(reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_WHAT_SELLING}))
    assert response.context_data['step_labels'] == views.SignupForTailoredContentWizardView.step_labels

    response = client.get(reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_PRODUCT_SEARCH}))
    assert response.context_data['step_labels'] == views.SignupForTailoredContentWizardView.step_labels

    response = client.get(reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_SIGN_UP}))
    assert response.context_data['step_labels'] == views.SignupForTailoredContentWizardView.step_labels


@pytest.mark.django_db
def test_signup_wizard_for_tailored_content_exposes_product_on_final_step(
    submit_signup_tailored_content_wizard_step, signup_wizard_steps_data, client
):
    search_data = signup_wizard_steps_data[views.STEP_PRODUCT_SEARCH]

    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_START])
    assert response.status_code == 302

    response = submit_signup_tailored_content_wizard_step(signup_wizard_steps_data[views.STEP_WHAT_SELLING])
    assert response.status_code == 302

    response = submit_signup_tailored_content_wizard_step(search_data)
    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['product_search_data'] == search_data


@pytest.mark.django_db
def test_signup_wizard_for_tailored_content_next_url(
    submit_signup_tailored_content_wizard_step, signup_wizard_steps_data
):
    response = submit_signup_tailored_content_wizard_step(
        data=signup_wizard_steps_data[views.STEP_START],
        params={'next': '/foo/bar/'},
    )
    assert response.status_code == 302
    assert response.url == '/signup/tailored-content/what-are-you-selling/?next=%2Ffoo%2Fbar%2F'

    response = submit_signup_tailored_content_wizard_step(
        data=signup_wizard_steps_data[views.STEP_WHAT_SELLING],
        params={'next': '/foo/bar/'},
    )
    assert response.status_code == 302
    assert response.url == '/signup/tailored-content/product-search/?next=%2Ffoo%2Fbar%2F'

    response = submit_signup_tailored_content_wizard_step(
        data=signup_wizard_steps_data[views.STEP_PRODUCT_SEARCH],
        params={'next': '/foo/bar/'},
    )
    assert response.status_code == 302
    assert response.url == '/signup/tailored-content/sign-up/?next=%2Ffoo%2Fbar%2F'


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_company_profile')
def test_set_company_name_success(mock_update_company_profile, mock_get_company_profile, client, user):
    mock_update_company_profile.return_value = create_response()
    mock_get_company_profile.return_value = {'foo': 'bar'}
    client.force_login(user)

    response = client.post(reverse('core:set-company-name'), {'name': 'Example corp'})
    assert response.status_code == 302
    assert response.url == cms_slugs.DASHBOARD_URL
    assert mock_update_company_profile.call_count == 1
    assert mock_update_company_profile.call_args == mock.call(
        data={'name': 'Example corp'},
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
@mock.patch.object(helpers, 'update_company_profile')
def test_set_company_name_success_with_next(mock_update_company_profile, mock_get_company_profile, client, user):
    mock_update_company_profile.return_value = create_response()
    mock_get_company_profile.return_value = {'foo': 'bar'}
    client.force_login(user)

    url = reverse('core:set-company-name')
    response = client.post(f'{url}?next=/foo/bar/', {'name': 'Example corp'})
    assert response.status_code == 302
    assert response.url == '/foo/bar/'


@pytest.mark.django_db
def test_create_api_token(client, rf):
    response = client.get('/api/create-token/')
    assert response.data is not None
    assert response.status_code == 200


@pytest.mark.django_db
def test_auth_with_url(client, rf):
    response = client.get('/api/create-token/')
    token = response.data['token']

    response_2 = client.get(f'/signup/?enc={token}')
    assert response_2.status_code == 200


@pytest.mark.django_db
def test_auth_with_cookie(client, rf):
    response = client.get('/api/create-token/')
    token = response.data['token']

    response_2 = client.get(f'/signup/?enc={token}')
    assert response_2.status_code == 200

    response_3 = client.get('/signup/')
    assert response_3.status_code == 200


@pytest.mark.django_db
def test_bad_auth_with_url(client):
    response = client.get('/signup/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_auth_with_cookie(client):
    client.cookies = SimpleCookie({'beta-user': BETA_AUTH_TOKEN_PAST})
    response = client.get('/signup/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_auth_with_enc_token(client):
    response = client.get(f'/signup/?enc={BETA_AUTH_TOKEN_PAST}')
    assert response.status_code == 403


@pytest.mark.django_db
@mock.patch.object(helpers, 'search_commodity_by_term')
def test_check_view(mock_search_commodity_by_term, client):
    # mock the API response with the wrong hs code. Make sure we dont hit the actual API endpoint in every test run.
    mock_search_commodity_by_term.return_value = create_response(json_body={'data': {'hsCode': '923311'}})

    res = client.get('/api/check/').json()

    assert res['CCCE_API']['response_body'] == '923311'
    assert res['CCCE_API']['status'] == status.HTTP_200_OK
    assert res['status'] == status.HTTP_200_OK
    assert mock_search_commodity_by_term.call_count == 1


@pytest.mark.django_db
@mock.patch.object(helpers, 'search_commodity_by_term')
def test_check_view_external_error(mock_search_commodity_by_term, client):
    test_http_error = status.HTTP_504_GATEWAY_TIMEOUT
    # the external API is down
    mock_search_commodity_by_term.return_value = create_response(status_code=test_http_error)

    res = client.get('/api/check/').json()

    assert res['CCCE_API']['status'] == test_http_error
    assert res['status'] == status.HTTP_200_OK
    assert mock_search_commodity_by_term.call_count == 1


@pytest.mark.django_db
def test_compare_countries_page(mock_export_plan_detail_list, domestic_homepage, client, user, mock_get_user_profile):
    client.force_login(user)
    url = reverse('core:compare-countries')

    response = client.get(url)

    # Check that the page renders even if there is no dashboard definition in wagtail
    assert response.status_code == 200
    assert response.context_data['dashboard_components'] is None
    assert re.search(r'\\"product\\":true', response.context_data['data_tabs_enabled'])

    # Populate dashboard with a couple of routes and check context
    DomesticDashboardFactory(
        parent=domestic_homepage,
        slug='dashboard',
        components__0__route__route_type='learn',
        components__0__route__title='Learning title',
        components__0__route__body='Learning Body Text',
        components__0__route__button={'label': 'Start learning'},
        components__1__route__route_type='plan',
        components__1__route__title='Planning title',
        components__1__route__body='Planning Body Text',
        components__1__route__button={'label': 'Start planning'},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response.context_data['dashboard_components'][0].value['route_type'] == 'learn'
    assert response.context_data['dashboard_components'][1].value['route_type'] == 'plan'


@pytest.mark.django_db
def test_contact_us_form_prepopulate(client, user, mock_get_user_profile):
    client.force_login(user)
    url = reverse('core:contact-us-help')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context_data['form'].initial == {
        'email': user.email,
        'family_name': user.last_name,
        'given_name': user.first_name,
    }


@pytest.mark.parametrize('get_location_value', [{'country': 'UK'}, None])
@pytest.mark.django_db
@mock.patch.object(helpers, 'get_location')
@mock.patch.object(views.ContactUsHelpFormView.form_class, 'save')
def test_contact_us_help_notify_save_success(
    mock_save, mock_get_location, client, get_location_value, contact_form_data
):
    mock_get_location.return_value = get_location_value
    url = reverse('core:contact-us-help')
    response = client.post(url, contact_form_data)

    assert response.status_code == 302
    assert response.url == reverse('core:contact-us-success')
    assert mock_save.call_count == 2
    assert mock_save.call_args_list == [
        mock.call(
            email_address=settings.GREAT_SUPPORT_EMAIL,
            form_url='/contact-us/help/',
            sender={
                'email_address': contact_form_data['email'],
                'country_code': get_location_value['country'] if get_location_value else None,
                'ip_address': None,
            },
            template_id=settings.CONTACTUS_ENQURIES_SUPPORT_TEMPLATE_ID,
        ),
        mock.call(
            email_address=contact_form_data['email'],
            form_url='/contact-us/help/',
            template_id=settings.CONTACTUS_ENQURIES_CONFIRMATION_TEMPLATE_ID,
        ),
    ]


@pytest.mark.django_db
def test_service_removed_view(
    client,
    domestic_site,
    domestic_homepage,
):
    advice_topic_page = TopicLandingPageFactory(
        title='Advice',
        parent=domestic_homepage,
    )

    article_listing_page = ArticleListingPageFactory(
        parent=advice_topic_page,
        landing_page_title='Listing Page',
        title='Listing Page',
        hero_teaser='list one',
    )

    article_page_1 = ArticlePageFactory(
        article_title='test article 1',
        parent=advice_topic_page,
        slug='test-article-1',
    )

    article_page_2 = ArticlePageFactory(
        article_title='test article 2',
        parent=advice_topic_page,
        slug='test-article-2',
    )

    article_page_3 = ArticlePageFactory(
        article_title='test article 3 - child of listing page',
        parent=article_listing_page,
        slug='test-article-3',
    )

    for url_name, args_ in (
        ('core:triage-wizard', ['foo']),
        ('core:triage-start', []),
        ('core:custom-page', []),
    ):
        response = client.get(reverse(url_name, args=args_))
        assert response.status_code == 200
        assertTemplateUsed(response, 'domestic/service_no_longer_available.html')

        _content = str(response.content)
        assert article_listing_page.url in _content
        assert article_page_1.url in _content
        assert article_page_2.url in _content
        assert article_page_3.url not in _content  # because a child of the listing page


@pytest.mark.parametrize(
    'base_url, expected_sitemap_url',
    (
        (
            'https://great.gov.uk',
            'https://great.gov.uk/sitemap.xml',
        ),
        (
            'https://great.gov.uk/',
            'https://great.gov.uk/sitemap.xml',
        ),
    ),
)
@pytest.mark.django_db
def test_robots_txt(client, base_url, expected_sitemap_url):
    with override_settings(BASE_URL=base_url):
        resp = client.get(reverse('core:robots'))
        assert resp.status_code == 200

        assert resp.content == b''.join(
            [
                b'User-agent: *\n',
                b'\n',
                b'Disallow: /api/\n',
                b'Disallow: /activity-stream/\n',
                b'\n',
                b'User-agent: MJ12bot\n',
                b'Disallow: /\n',
                b'\n',
                b'User-agent: PetalBot\n',
                b'Disallow: /\n',
                b'\n',
                b'User-agent: Bytespider\n',
                b'Disallow: /\n',
                b'\n',
                f'Sitemap: {expected_sitemap_url}\n'.encode(),
            ]
        )


@pytest.mark.django_db
def test_serve_subtitles(client, user):
    media = make_test_video()

    media.subtitles_en = 'Dummy subtitles content'
    media.save()

    dest = reverse('core:subtitles-serve', args=[media.id, 'en'])

    client.force_login(user)
    resp = client.get(dest, follow=False)

    assert resp.status_code == 200
    assert resp.content == b'Dummy subtitles content'


@pytest.mark.django_db
def test_serve_subtitles__missing_media(client, user):
    dest = reverse('core:subtitles-serve', args=[99999, 'en'])
    client.force_login(user)
    resp = client.get(dest, follow=False)

    assert resp.status_code == 404


@pytest.mark.django_db
def test_serve_subtitles__none_available(client, user):
    media = make_test_video()
    media.save()

    dest = reverse('core:subtitles-serve', args=[media.id, 'en'])
    client.force_login(user)
    resp = client.get(dest, follow=False)

    assert resp.status_code == 404


@pytest.mark.django_db
def test_serve_subtitles__login_required(client):
    media = make_test_video()

    media.subtitles_en = 'Dummy subtitles content'
    media.save()

    dest = reverse('core:subtitles-serve', args=[media.id, 'en'])

    resp = client.get(dest, follow=False)

    assert resp.status_code == 302

    assert resp.headers['location'] == reverse('core:login') + f'?next={dest}'


class TestMicrositeLocales(TestCase):
    def setUp(self):
        self.client = Client()
        self.en_locale = Locale.objects.get_or_create(language_code='en-gb')
        self.es_locale = Locale.objects.get_or_create(language_code='es')
        self.fr_locale = Locale.objects.get_or_create(language_code='fr')
        self.pt_locale = Locale.objects.get_or_create(language_code='pt')
        self.ko_locale = Locale.objects.get_or_create(language_code='ko')
        self.zh_locale = Locale.objects.get_or_create(language_code='zh-cn')
        self.ms_locale = Locale.objects.get_or_create(language_code='ms')

    @pytest.fixture(autouse=True)
    def domestic_homepage_fixture(self, domestic_homepage):
        self.domestic_homepage = domestic_homepage

    @pytest.fixture(autouse=True)
    def en_microsite(self):
        root = MicrositeFactory(title='root', slug='microsites', parent=self.domestic_homepage)
        self.en_microsite = MicrositePageFactory(
            page_title='microsite home title en-gb',
            page_subheading='a microsite subheading en-gb',
            slug='microsite-page-home',
            parent=root,
        )
        Site.objects.create(hostname='greatcms.trade.great', root_page=root, site_name='Great', is_default_site=True)
        self.url = reverse_lazy('core:microsites', kwargs={'page_slug': '/microsite-page-home'})

    def test_correct_translation_english(self):
        response = self.client.get(self.url)
        html_response = response.content.decode('utf-8')
        assert 'microsite home title en-gb' in html_response and 'a microsite subheading en-gb' in html_response

    def test_correct_translation_for_spanish(self):
        site_es = self.en_microsite.copy_for_translation(self.es_locale[0], copy_parents=True)
        site_es.page_title = 'página de inicio del micrositio'
        site_es.page_subheading = 'Subtítulo de la Página de Inicio del Micrositio'

        site_es.save()
        revision = site_es.save_revision()
        revision.publish()
        spanish_site = Site.objects.get(hostname='greatcms.trade.great')
        spanish_site.root_page = site_es.get_parent()
        spanish_site.save()

        url_spanish = self.url + '?lang=es'
        response = self.client.get(url_spanish, HTTP_ACCEPT_LANGUAGE='es')
        html_response = response.content.decode('utf-8')
        assert 'página de inicio del micrositio' in html_response
        assert 'Subtítulo de la Página de Inicio del Micrositio' in html_response

    def test_correct_translation_french(self):
        site_fr = self.en_microsite.copy_for_translation(self.fr_locale[0], copy_parents=True)
        site_fr.page_title = 'page d&amp;#x27;accueil du microsite'
        site_fr.page_subheading = 'Sous-titre de la page d&#x27;accueil du microsite'

        site_fr.save()
        revision = site_fr.save_revision()
        revision.publish()
        french_site = Site.objects.get(hostname='greatcms.trade.great')
        french_site.root_page = site_fr.get_parent()
        french_site.save()

        url_french = self.url + '?lang=fr'
        response = self.client.get(url_french)
        html_response = response.content.decode('utf-8')
        assert 'page d&amp;#x27;accueil du microsite' in html_response
        assert 'Sous-titre de la page d&amp;#x27;accueil du microsite' in html_response

    def test_correct_translation_portguese(self):
        site_pt = self.en_microsite.copy_for_translation(self.pt_locale[0], copy_parents=True)
        site_pt.page_title = 'página inicial do microsite'
        site_pt.page_subheading = 'Subtítulo de la Página de Inicio del Micrositio'

        site_pt.save()
        revision = site_pt.save_revision()
        revision.publish()
        portguese_site = Site.objects.get(hostname='greatcms.trade.great')
        portguese_site.root_page = site_pt.get_parent()
        portguese_site.save()

        url_portugeuse = self.url + '?lang=pt'
        response = self.client.get(url_portugeuse)
        html_response = response.content.decode('utf-8')
        assert (
            'página inicial do microsite' in html_response
            and 'Subtítulo de la Página de Inicio del Micrositio' in html_response  # noqa: W503
        )

    def test_correct_translation_korean(self):
        site_ko = self.en_microsite.copy_for_translation(self.ko_locale[0], copy_parents=True)
        site_ko.page_title = '페이지 제목: 무역 기회 창출: 영국-대한민국 수출 포럼'
        site_ko.page_subheading = '부제: 국제 무역과 경제 성장을 위한 강력한 동반자관계 구축'
        site_ko.save()

        revision = site_ko.save_revision()
        revision.publish()
        korean_site = Site.objects.get(hostname='greatcms.trade.great')
        korean_site.root_page = site_ko.get_parent()
        korean_site.save()

        url_korean = self.url + '?lang=ko'
        response = self.client.get(url_korean)
        html_response = response.content.decode('utf-8')
        assert (
            '페이지 제목: 무역 기회 창출: 영국-대한민국 수출 포럼' in html_response
            and '부제: 국제 무역과 경제 성장을 위한 강력한 동반자관계 구축' in html_response  # noqa: W503
        )

    def test_correct_translation_mandarin(self):
        site_zh = self.en_microsite.copy_for_translation(self.zh_locale[0], copy_parents=True)
        site_zh.page_title = '微型网站首页'
        site_zh.page_subheading = '微型网站主页字幕'
        site_zh.save()

        revision = site_zh.save_revision()
        revision.publish()
        mandarin_site = Site.objects.get(hostname='greatcms.trade.great')
        mandarin_site.root_page = site_zh.get_parent()
        mandarin_site.save()

        url_mandarin = self.url + '?lang=zh-cn'
        response = self.client.get(url_mandarin)
        html_response = response.content.decode('utf-8')
        assert site_zh.page_title in html_response and site_zh.page_subheading in html_response  # noqa: W503

    def test_correct_translation_malay(self):
        site_ms = self.en_microsite.copy_for_translation(self.ms_locale[0], copy_parents=True)
        site_ms.page_title = 'laman utama laman mikro'
        site_ms.page_subheading = 'Sarikata Halaman Utama Microsite'
        site_ms.save()

        revision = site_ms.save_revision()
        revision.publish()
        malay_site = Site.objects.get(hostname='greatcms.trade.great')
        malay_site.root_page = site_ms.get_parent()
        malay_site.save()

        url_malay = self.url + '?lang=ms'
        response = self.client.get(url_malay)
        html_response = response.content.decode('utf-8')
        assert site_ms.page_title in html_response and site_ms.page_subheading in html_response  # noqa: W503

    def test_fall_back_to_english_for_unimplemented_enabled_language(self):
        url = reverse_lazy('core:microsites', kwargs={'page_slug': '/microsite-page-home'})

        url_arabic = url + '?lang=ar'
        response = self.client.get(url_arabic)
        html_response = response.content.decode('utf-8')
        assert 'microsite home title en-gb' in html_response and 'a microsite subheading en-gb' in html_response

    def test_fall_back_to_english_for_unimplemented_language(self):
        url = reverse_lazy('core:microsites', kwargs={'page_slug': '/microsite-page-home'})
        url_za = url + '?lang=za'

        response = self.client.get(url_za)
        html_response = response.content.decode('utf-8')
        assert 'microsite home title en-gb' in html_response and 'a microsite subheading en-gb' in html_response


@pytest.mark.django_db
def test_correct_footer_location_link_domestic():
    campaign_view = CampaignView()
    campaign_view.location = {'country': 'GB'}
    assert campaign_view._get_request_location_link() == '/'


def test_correct_footer_location_link_international():
    campaign_view = CampaignView()
    campaign_view.location = {'country': 'ES'}
    assert campaign_view._get_request_location_link() == '/internatonal/'


@pytest.fixture
def image_user(django_user_model):
    return django_user_model.objects.create_user(
        username='username',
        password='password',
        is_staff=True,
    )


@mock.patch.object(views.AltImageUploadView, 'get_creation_form')
@mock.patch('wagtail.images.views.chooser.find_image_duplicates')
@mock.patch.object(SelectFormatResponseMixin, 'render_select_format_response')
@pytest.mark.django_db
def test_alt_image_upload_view_select_format_true_not_duplicate(
    mock_render_select_format_response,
    mock_find_image_duplicates,
    mock_get_creation_form,
    image_data,
    image_user,
    rf,
):
    mock_get_creation_form.return_value.is_valid.return_value = True
    id = image_data['files']['image-chooser-upload-file'].id
    alt_text = image_data['image-chooser-upload-alt_text'][0]
    mock_get_creation_form.return_value.save.return_value = MagicMock(id=id, alt_text=alt_text)
    mock_find_image_duplicates.return_value.first.return_value = None
    expected_result = {'step': 'select_format', 'html': '<html>Test Image</html>'}
    mock_render_select_format_response.return_value = JsonResponse(status=200, data=expected_result)
    request = rf.post('/admin/images/chooser/create/?select_format=true', data=image_data)

    image_user.is_superuser = True
    image_user.save()
    request.user = image_user
    response = views.AltImageUploadView.as_view()(request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    assert json.loads(response.content.decode('utf8')) == expected_result


@mock.patch.object(views.AltImageUploadView, 'get_creation_form')
@mock.patch('wagtail.images.views.chooser.find_image_duplicates')
@mock.patch.object(ChosenResponseMixin, 'get_chosen_response')
@pytest.mark.django_db
def test_alt_image_upload_view_select_format_false_not_duplicate(
    mock_get_chosen_response,
    mock_find_image_duplicates,
    mock_get_creation_form,
    image_data,
    image_user,
    rf,
):
    mock_get_creation_form.return_value.is_valid.return_value = True
    id = image_data['files']['image-chooser-upload-file'].id
    alt_text = image_data['image-chooser-upload-alt_text'][0]
    title = image_data['image-chooser-upload-title'][0]
    width = image_data['image-chooser-upload-focal_point_width'][0]
    height = image_data['image-chooser-upload-focal_point_height'][0]
    expected_result = {
        'id': id,
        'title': title,
        'edit_url': f'/admin/images/{id}/',
        'preview': {'url': f'/admin/images/{id}/', 'width': width, 'height': height},
    }
    mock_get_creation_form.return_value.save.return_value = MagicMock(id=id, alt_text=alt_text)
    mock_get_chosen_response.return_value = JsonResponse(status=200, data={'step': 'chosen', 'result': expected_result})
    mock_find_image_duplicates.return_value.first.return_value = None
    request = rf.post('/admin/images/chooser/create', data=image_data)
    image_user.is_superuser = True
    image_user.save()
    request.user = image_user
    response = views.AltImageUploadView.as_view()(request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    response_json = json.loads(response.content.decode('utf8'))
    assert response_json['step'] == 'chosen'
    assert response_json['result'] == expected_result


@mock.patch.object(views.AltImageUploadView, 'get_creation_form')
@mock.patch('wagtail.images.views.chooser.find_image_duplicates')
@mock.patch.object(ImageUploadViewMixin, 'render_duplicate_found_response')
@pytest.mark.django_db
def test_alt_image_upload_view_select_format_false_is_duplicate(
    mock_render_duplicate_found_response, mock_find_image_duplicates, mock_get_creation_form, image_data, image_user, rf
):
    mock_get_creation_form.return_value.is_valid.return_value = True
    id = image_data['files']['image-chooser-upload-file'].id
    alt_text = image_data['image-chooser-upload-alt_text'][0]
    create_form_return = MagicMock(id=id, alt_text=alt_text)
    mock_get_creation_form.return_value.save.return_value = create_form_return
    mock_find_image_duplicates.return_value.first.return_value = create_form_return
    mock_render_duplicate_found_response.return_value = JsonResponse(status=200, data={'step': 'duplicate_found'})
    request = rf.post('/admin/images/chooser/create?select_format=true', data=image_data)
    image_user.is_superuser = True
    image_user.save()
    request.user = image_user
    response = views.AltImageUploadView.as_view()(request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    assert json.loads(response.content.decode('utf8'))['step'] == 'duplicate_found'


@mock.patch.object(views.AltImageUploadView, 'get_creation_form')
@mock.patch.object(CreateViewMixin, 'get_reshow_creation_form_response')
@pytest.mark.django_db
def test_alt_image_upload_view_form_is_invalid(
    mock_get_reshow_creation_form_response, mock_get_creation_form, image_data, image_user, rf
):
    mock_get_creation_form.return_value.is_valid.return_value = False
    mock_get_reshow_creation_form_response.return_value = JsonResponse(
        status=200, data={'step': 'reshow_creation_form'}
    )
    request = rf.post('/admin/images/chooser/create?select_format=true', data=image_data)
    image_user.is_superuser = True
    image_user.save()
    request.user = image_user
    response = views.AltImageUploadView.as_view()(request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    assert json.loads(response.content.decode('utf8'))['step'] == 'reshow_creation_form'


@pytest.mark.django_db
def test_design_system_page(
    client,
):
    response = client.get(reverse('core:design-system'))

    assert 'GREAT Design System' in str(response.rendered_content)


@pytest.mark.django_db
def test_market_selection_page(
    client,
):
    response = client.get(reverse('core:product-market') + '?product=gin', follow=True)

    assert 'Where do you want to sell your gin?' in str(response.rendered_content)
    assert 'Find and compare markets for selling gin' in str(response.rendered_content)
    assert 'You sell gin' in str(response.rendered_content)


@pytest.mark.django_db
def test_market_results_page(
    client,
):
    response = client.get(reverse('core:product-market') + '?product=gin&market=germany', follow=True)

    assert 'Selling gin to Germany' in str(response.rendered_content)
    assert 'You want to sell gin to Germany' in str(response.rendered_content)
    assert 'Exporting guide to Germany' in str(response.rendered_content)
    assert ('Germany is one of the world’s largest economies') in str(response.rendered_content)


@pytest.mark.django_db
def test_market_selection_with_no_product_page(
    client,
):
    response = client.get(reverse('core:product-market'), follow=True)

    assert 'Where do you want to sell?' in str(response.rendered_content)


@pytest.mark.django_db
@mock.patch.object(actions, 'SaveOnlyInDatabaseAction')
def test_post_with_both_product_and_market(mock_save_action, client):
    post_data = {'product': 'gin', 'market-input': 'Germany'}
    response = client.post(reverse('core:product-market'), data=post_data)
    expected_redirect_url = reverse_lazy('core:product-market') + '?product=gin&market=germany'

    assert response.status_code == 302
    assert response.url == expected_redirect_url

    mock_save_action.assert_called_once_with(
        full_name='Anonymous user',
        subject='Product and Market experiment',
        email_address='anonymous-user@test.com',
        form_url='/product-market',
    )

    expected_data = {'product': 'gin', 'market': 'Germany', 'userid': mock.ANY}
    mock_save_action.return_value.save.assert_called_once_with(expected_data)


@pytest.mark.django_db
@modify_settings(SAFELIST_HOSTS={'append': 'www.safe.com'})
def test_signup_for_tailored_content_wizard_view_next_url(client):
    response1 = client.get(reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START}))
    assert 'next_url' not in response1.context_data

    response2 = client.get(
        reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START})
        + '?next=http://www.unsafe.com'
    )
    assert response2.context_data['next_url'] == '/'

    response3 = client.get(
        reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START}) + '?next=http://www.safe.com'
    )
    assert response3.context_data['next_url'] == 'http://www.safe.com'


@pytest.mark.django_db
def test_signup_view(client):
    response = client.get(
        reverse(
            'core:signup',
        ),
        HTTP_REFERER='http:anyurl.com',
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_pingdom_database_healthcheck_ok(client):
    response = client.get(reverse('core:pingdom'))
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(DatabaseHealthCheck, 'check')
def test_pingdom_database_healthcheck_false(mock_database_check, client):
    mock_database_check.return_value = (
        False,
        'Database Error',
    )
    response = client.get(reverse('core:pingdom'))
    assert response.status_code == 500


@pytest.mark.django_db
def test_csat_user_feedback_with_session_value(
    client,
    user,
):
    client.force_login(user)
    url = reverse_lazy('core:product-market') + '?product=gin&market=germany'

    HCSAT.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['export_academy_csat_id'] = 1
    session.save()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_csat_user_feedback_submit(
    client,
    user,
):
    client.force_login(user)
    url = reverse_lazy('core:product-market') + '?product=gin&market=germany'

    HCSAT.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['export_academy_csat_id'] = 1
    session['user_journey'] = 'DASHBOARD'
    session.save()
    response = client.post(
        url,
        {
            'satisfaction': 'SATISFIED',
            'user_journey': 'DASHBOARD',
            'experience': ['NOT_FIND_LOOKING_FOR'],
            'likelihood_of_return': 'LIKELY',
        },
    )
    assert response.status_code == 302


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url',
    (
        (
            reverse('core:guided-journey-step-1'),
            {
                'sic_description': 'Production of coffee and coffee substitutes',
                'make_or_do_keyword': 'coffee',
                'sector': 'Food and drink',
                'exporter_type': 'goods',
            },
            reverse('core:guided-journey-step-2'),
        ),
        (
            reverse('core:guided-journey-step-1-edit') + '?return_to_step=3',
            {
                'sic_description': 'Tea processing',
                'make_or_do_keyword': 'tea',
                'sector': 'Food and drink',
                'exporter_type': 'goods',
            },
            reverse('core:guided-journey-step-2-edit') + '?return_to_step=3',
        ),
        (
            reverse('core:guided-journey-step-1-edit') + '?return_to_step=3',
            {
                'sic_description': 'Tax consultancy',
                'make_or_do_keyword': 'tax',
                'sector': 'Financial and professional services',
                'exporter_type': 'service',
            },
            reverse('core:guided-journey-step-3'),
        ),
        (
            reverse('core:guided-journey-step-2'),
            {
                'hs_code': '1234567890',
                'commodity_name': 'coffee beans',
            },
            reverse('core:guided-journey-step-3'),
        ),
        (
            reverse('core:guided-journey-step-3'),
            {
                'market': 'Mexico',
            },
            reverse('core:guided-journey-step-4'),
        ),
        (
            reverse('core:guided-journey-step-3-edit') + '?return_to_step=4',
            {
                'market': 'China',
            },
            reverse('core:guided-journey-step-4'),
        ),
    ),
)
@pytest.mark.django_db
def test_guided_journey_as_goods_exporter(page_url, form_data, redirect_url, client):
    response = client.post(
        page_url,
        form_data,
    )

    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url',
    (
        (
            reverse('core:guided-journey-step-1'),
            {
                'sic_description': 'Information technology consultancy activities',
                'make_or_do_keyword': 'consult',
                'sector': 'Technology and smart cities',
                'exporter_type': 'service',
            },
            reverse('core:guided-journey-step-3'),
        ),
        (
            reverse('core:guided-journey-step-1-edit') + '?return_to_step=3',
            {
                'sic_description': 'Tax consultancy',
                'make_or_do_keyword': 'tax',
                'sector': 'Financial and professional services',
                'exporter_type': 'service',
            },
            reverse('core:guided-journey-step-3'),
        ),
        (
            reverse('core:guided-journey-step-3'),
            {
                'market': 'Mexico',
            },
            reverse('core:guided-journey-step-4'),
        ),
        (
            reverse('core:guided-journey-step-3-edit') + '?return_to_step=4',
            {
                'market': 'China',
            },
            reverse('core:guided-journey-step-4'),
        ),
    ),
)
@pytest.mark.django_db
def test_guided_journey_as_service_exporter(
    page_url,
    form_data,
    redirect_url,
    client,
):
    response = client.post(
        page_url,
        form_data,
    )

    assert response.status_code == 302
    assert response.url == redirect_url
