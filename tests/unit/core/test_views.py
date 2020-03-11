from unittest import mock
from unittest.mock import patch, Mock
import json

from directory_constants import choices
import pytest

from django.urls import reverse

from core import helpers
from tests.helpers import create_response
from directory_api_client import api_client


@pytest.fixture
def company_data():
    return {
        'company_name': 'Example corp',
        'expertise_industries': json.dumps(['Science']),
        'expertise_countries': json.dumps(['USA']),
        'first_name': 'foo',
        'last_name': 'bar',
    }


@pytest.fixture(autouse=True)
def mock_get_company_profile():
    stub = mock.patch('sso.helpers.get_company_profile', return_value=None)
    yield stub.start()
    stub.stop()


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
            'company_name': 'Example corp',
            'expertise_industries': ['Science'],
            'expertise_countries': ['USA'],
            'first_name': 'foo',
            'last_name': 'bar'
        },
        sso_session_id=user.session_id,
    )


@pytest.mark.django_db
def test_api_update_company_not_logged_in(client, company_data):
    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_update_company_no_company(client, user, company_data):
    client.force_login(user)

    response = client.post(reverse('core:api-update-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_company_profile')
@mock.patch.object(helpers, 'create_user_profile')
def test_api_create_company_success(mock_create_user_profile, mock_create_company_profile, client, user, company_data):
    client.force_login(user)

    mock_create_user_profile.return_value = create_response()
    mock_create_company_profile.return_value = create_response()

    response = client.post(reverse('core:api-create-company'), company_data)
    assert response.status_code == 200
    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'foo', 'last_name': 'bar'},
        sso_session_id=user.session_id,
    )
    assert mock_create_company_profile.call_count == 1
    assert mock_create_company_profile.call_args == mock.call({
        'sso_id': user.id,
        'company_name': company_data['company_name'],
        'expertise_industries': company_data['expertise_industries'],
        'expertise_countries': company_data['expertise_countries'],
        'company_email': user.email,
        'contact_email_address': user.email,
    })


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_company_profile')
@mock.patch.object(helpers, 'create_user_profile')
def test_api_create_company_validation_error(mock_create_user_profile, mock_create_company_profile, client, user):
    client.force_login(user)

    response = client.post(reverse('core:api-create-company'), {})

    assert response.status_code == 400
    assert mock_create_user_profile.call_count == 0
    assert mock_create_company_profile.call_count == 0


@pytest.mark.django_db
def test_api_create_company_not_logged_in(client, company_data):
    response = client.post(reverse('core:api-create-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_api_create_company_already_has_company(mock_get_company_profile, client, user, company_data):
    mock_get_company_profile.return_value = {'foo': 'bar'}

    client.force_login(user)

    response = client.post(reverse('core:api-create-company'), company_data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_landing_page_logged_in(client, user):
    client.force_login(user)

    url = reverse('core:landing-page')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('core:dashboard')


@pytest.mark.django_db
@mock.patch.object(api_client.personalisation, 'events_by_location_list')
@mock.patch.object(api_client.personalisation, 'export_opportunities_by_relevance_list')
def test_dashboard_page_logged_in(
    mock_events_by_location_list,
    mock_export_opportunities_by_relevance_list,
    client,
    user
):
    mock_events_by_location_list.return_value = create_response(json_body={'results': []})
    mock_export_opportunities_by_relevance_list.return_value = create_response(json_body={'results': []})
    client.force_login(user)

    url = reverse('core:dashboard')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_page_not_logged_in(client, user):
    url = reverse('core:landing-page')

    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_apis_ok(client, user):

    with patch(
        'directory_api_client.api_client.personalisation.events_by_location_list'
    ) as events_api_results:
        events_api_results.return_value = Mock(status_code=200, **{'json.return_value': {
            'results': [{
                'name': 'Global Aid and Development Directory',
                'content': 'DIT is producing a directory of companies \
who supply, or would like to supply, relevant humanitarian aid \
and development products and services to the United Nations \
family of organisations and NGOs.  ',
                'location': {'city': 'London'},
                'url': 'www.example.com',
                'date': '2020-06-06'
            }, {
                'name': 'Less Info',
                'content': 'Content',
                'url': 'www.example.com',
            }]
        }})

        with patch(
            'directory_api_client.api_client.\
personalisation.export_opportunities_by_relevance_list'
        ) as exops_api_results:
            exops_api_results.return_value = Mock(status_code=200, **{'json.return_value': {
                'results': [{'title': 'French sardines required',
                             'url': 'http://exops.trade.great:3001/\
export-opportunities/opportunities/french-sardines-required',
                             'description': 'Nam dolor nostrum distinctio.Et quod itaque.',
                             'published_date': '2020-01-14T15:26:45.334Z',
                             'closing_date': '2020-06-06',
                             'source': 'post'}]
            }})

            client.force_login(user)

            url = reverse('core:dashboard')

            response = client.get(url)

            assert response.status_code == 200
            assert response.context_data['events'] == [{
                'title': 'Global Aid and Development Directory',
                'description': 'DIT is producing a directory of compani…',
                'url': 'www.example.com',
                'location': 'London',
                'date': '06 Jun 2020'
            }, {
                'title': 'Less Info',
                'description': 'Content',
                'url': 'www.example.com',
                'location': 'n/a',
                'date': 'n/a'
            }]
            assert response.context_data['export_opportunities'] == [{
                'title': 'French sardines required',
                'description': 'Nam dolor nostrum distinctio.…',
                'source': 'post',
                'url': 'http://exops.trade.great:3001/export-opportunities\
/opportunities/french-sardines-required',
                'published_date': '14 Jan 2020',
                'closing_date': '06 Jun 2020'
            }]


@pytest.mark.django_db
def test_dashboard_apis_fail(client, user):
    with patch(
        'directory_api_client.api_client.personalisation.events_by_location_list'
    ) as events_api_results:
        events_api_results.return_value = Mock(status_code=500, **{'json.return_value': {}})

        with patch(
            'directory_api_client.api_client.\
personalisation.export_opportunities_by_relevance_list'
        ) as exops_api_results:
            exops_api_results.return_value = Mock(status_code=500, **{'json.return_value': {}})

            client.force_login(user)

            url = reverse('core:dashboard')

            response = client.get(url)

            assert response.status_code == 200
            assert response.context_data['events'] == []
            assert response.context_data['export_opportunities'] == []


@pytest.mark.django_db
def test_capability_article_logged_in(client, user):
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
    assert response.url == reverse('core:landing-page') + f'?next={url}'


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
    assert response.url == reverse('core:dashboard')


@mock.patch.object(helpers, 'get_markets_page_title')
def test_markets_logged_in(mock_get_markets_page_title, mock_get_company_profile, user, client):
    mock_get_markets_page_title.return_value = 'Some page title'
    mock_get_company_profile.return_value = {
        'expertise_countries': ['AF'], 'expertise_industries': [choices.SECTORS[0][0]]
    }
    client.force_login(user)
    url = reverse('core:markets')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['page_title'] == 'Some page title'
    assert len(response.context_data['most_popular_countries']) == 5


def test_markets_not_logged_in(mock_get_company_profile, client):
    url = reverse('core:markets')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['page_title'] is None
    assert response.context_data['most_popular_countries'] is None
