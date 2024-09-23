import pytest
from django.template.loader import render_to_string
from great_components.context_processors import urls_processor

pytestmark = pytest.mark.django_db


def test_cms_guidance_descriptive_page_title_is_rendered(rf):
    context = urls_processor(None)

    context['request'] = rf.get('/')
    cms_snippet = {
        'title': 'Descriptive text',
    }
    context['content_snippet'] = cms_snippet
    context.update(urls_processor(None))
    html = render_to_string('domestic/contact/guidance.html', context)

    assert cms_snippet['title'] in html
