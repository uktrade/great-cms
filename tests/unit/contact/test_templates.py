import pytest
from django.template.loader import render_to_string
from great_components.context_processors import urls_processor

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.contact,
]


def test_contact_domestic_descriptive_page_title_override_is_rendered():
    context = urls_processor(None)
    html = render_to_string('domestic/contact/step.html', context)

    assert 'Tell us how we can help - great.gov.uk' in html


def test_cms_guidance_descriptive_page_title_is_rendered(rf):
    context = urls_processor(None)

    context['request'] = rf.get('/')
    cms_snippet = {
        'title': 'Descriptive text',
    }
    context['content_snippet'] = cms_snippet
    context.update(urls_processor(None))
    html = render_to_string('domestic/contact/guidance.html', context)

    assert cms_snippet['title'] + ' - great.gov.uk' in html
