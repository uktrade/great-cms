import pytest
from django.http import HttpRequest
from django.template.loader import render_to_string

pytestmark = pytest.mark.django_db


def render_html(email_alerts):
    http_request = HttpRequest()
    http_request.META['HTTP_HOST'] = 'example.com'
    http_request.META['SERVER_PORT'] = '8080'
    context = {'exops_data': {'email_alerts': email_alerts}, 'request': http_request}
    return render_to_string('exops/is-exops-user-email-alerts.html', context)


def test_email_alert_title():
    html = render_html([{'title': 'This is a title', 'created_on': '2000-01-01T01:01:01.000001Z'}])

    assert 'This is a title' in html


def test_email_alert_with_term():
    html = render_html([{'term': '--example term--', 'created_on': '2000-01-01T01:01:01.000001Z'}])

    assert '--example term-- in all countries' in html


def test_email_alert_term_country():
    html = render_html([{'term': 'Sports', 'created_on': '2000-01-01T01:01:01.000001Z', 'countries': ['UK,Spain']}])

    assert 'Sports in UK,Spain' in html


def test_email_alert_country():
    html = render_html([{'created_on': '2000-01-01T01:01:01.000001Z', 'countries': ['UK,Spain']}])

    assert 'all opportunities in UK,Spain' in html


def test_email_alert_all_opportunities():
    html = render_html([{'created_on': '2000-01-01T01:01:01.000001Z'}])

    assert 'all opportunities' in html


def test_email_alert_link_region():
    html = render_html([{'created_on': '2000-01-01T01:01:01.000001Z', 'countries': ['Greece', 'Italy']}])
    assert 'href="?suppress_subscription_block=true&s=&countries[]=Greece&countries[]=Italy' in html
