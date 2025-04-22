import pytest
from directory_components.context_processors import urls_processor
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse


@pytest.mark.django_db
def test_company_verify_hub_letter_sent():
    http_request = HttpRequest()
    http_request.META["HTTP_HOST"] = 'example.com'
    http_request.META["SERVER_PORT"] = '8080'
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': True,
        },
        'request': http_request,
    }
    context.update(urls_processor(http_request))
    assert 'feedback' in context['services_urls']
    html = render_to_string(template_name, context)
    assert reverse('find_a_buyer:verify-company-address-confirm') in html
    assert reverse('find_a_buyer:verify-companies-house') in html


@pytest.mark.django_db
def test_company_verify_hub_letter_not_sent():
    http_request = HttpRequest()
    http_request.META["HTTP_HOST"] = 'example.com'
    http_request.META["SERVER_PORT"] = '8080'
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': False,
        },
        'request': http_request,
    }
    context.update(urls_processor(http_request))
    assert 'feedback' in context['services_urls']
    html = render_to_string(template_name, context)

    assert reverse('find_a_buyer:verify-company-address') in html
    assert reverse('find_a_buyer:verify-companies-house') in html
