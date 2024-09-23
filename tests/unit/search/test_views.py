from unittest.mock import call, patch

import pytest
from django.test import RequestFactory, modify_settings
from django.urls import reverse
from freezegun import freeze_time
from wagtail.models import Page
from wagtail.search.backends import get_search_backend

from search import views

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
@patch('wagtail.search.backends.get_search_backend')
def test_search_view(mock_get_search_backend):
    # Mock the search backend
    mock_search_backend = mock_get_search_backend.return_value
    mock_search_backend.search.return_value = Page.objects.none()

    # Create test data
    home_page = Page.objects.get(slug='home')
    test_page1 = home_page.add_child(instance=Page(title='Test Page 1', slug='test-page-1'))
    test_page2 = home_page.add_child(instance=Page(title='Another Test Page', slug='another-test-page'))

    # Refresh the search index
    search_backend = get_search_backend()
    search_backend.refresh_index()

    # Perform search
    search_results = Page.objects.search('Test Page')

    # Assert that the search results contain the expected pages
    assert test_page1 in search_results
    assert test_page2 in search_results

    # Perform a search that should return no results
    search_results_empty = Page.objects.search('Nonexistent Page')
    assert not search_results_empty

    # Verify that the search method was called
    mock_search_backend.search.assert_called()


def test_search_feedback_view(client):
    response = client.get(reverse('search:feedback'))
    assert response.status_code == 200


@patch.object(views.SearchFeedbackFormView.form_class, 'save')
@freeze_time('2020-01-01')
def test_search_feedback_submit_success(mock_save, client, captcha_stub):
    url = reverse('search:feedback')

    # With contact details
    data = {
        'result_found': 'no',
        'search_target': 'Test',
        'reason_for_site_visit': 'Test',
        'from_search_query': 'hello',
        'from_search_page': 1,
        'contactable': 'yes',
        'contact_name': 'Test',
        'contact_email': 'test@example.com',
        'contact_number': '55512341234',
        'g-recaptcha-response': captcha_stub,
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == f"{reverse('search:search')}?page=1&q=hello&submitted=true"

    assert mock_save.call_count == 1
    assert mock_save.call_args == call(
        email_address='test@example.com',
        full_name='Test',
        subject='Search Feedback - 00:00 01 Jan 2020',
        form_url='/search/feedback/',
    )


@patch.object(views.SearchFeedbackFormView.form_class, 'save')
@freeze_time('2020-01-01')
def test_search_feedback_form_success_with_next_parameter(mock_save, client, captcha_stub):
    url = reverse('search:feedback') + '?next=/'

    # No contact details
    data = {
        'result_found': 'no',
        'search_target': 'Test',
        'reason_for_site_visit': 'Test',
        'from_search_query': '',
        'from_search_page': '',
        'contactable': 'no',
        'g-recaptcha-response': captcha_stub,
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == f"{reverse('search:feedback-success')}?next=/"

    assert mock_save.call_count == 1
    assert mock_save.call_args == call(
        email_address='emailnotgiven@example.com',
        full_name='Name not given',
        subject='Search Feedback - 00:00 01 Jan 2020',
        form_url='/search/feedback/?next=/',
    )


@modify_settings(SAFELIST_HOSTS={'append': 'www.safe.com'})
def test_search_feedback_success_view_next_url():
    request1 = RequestFactory().get('')
    response1 = views.SearchFeedbackSuccessView.as_view()(request1)
    assert 'next_url' not in response1.context_data

    request2 = RequestFactory().get('/?next=http://www.unsafe.com')
    response2 = views.SearchFeedbackSuccessView.as_view()(request2)
    assert response2.context_data['next_url'] == '/'

    request3 = RequestFactory().get('/?next=http://www.safe.com')
    response3 = views.SearchFeedbackSuccessView.as_view()(request3)
    assert response3.context_data['next_url'] == 'http://www.safe.com'
