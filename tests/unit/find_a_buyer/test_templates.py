import pytest
from directory_components.context_processors import urls_processor
from django.template.loader import render_to_string
from django.urls import reverse


@pytest.mark.django_db
def test_company_verify_hub_letter_sent(rf):
    request = rf.get('/')
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': True,
        }
    }
    context.update(urls_processor(request))
    assert 'feedback' in context['services_urls']
    html = render_to_string(template_name, context)
    assert reverse('find_a_buyer:verify-company-address-confirm') in html
    assert reverse('find_a_buyer:verify-companies-house') in html


@pytest.mark.django_db
def test_company_verify_hub_letter_not_sent(rf):
    request = rf.get('/')
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': False,
        }
    }
    context.update(urls_processor(request))
    assert 'feedback' in context['services_urls']
    html = render_to_string(template_name, context)

    assert reverse('find_a_buyer:verify-company-address') in html
    assert reverse('find_a_buyer:verify-companies-house') in html
