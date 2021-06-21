import pytest
from django.template.loader import render_to_string
from great_components.context_processors import urls_processor

pytestmark = pytest.mark.django_db


def test_contact_domestic_descriptive_page_title_override_is_rendered():
    context = urls_processor(None)
    html = render_to_string('domestic/contact/step.html', context)

    assert 'Tell us how we can help - great.gov.uk' in html
