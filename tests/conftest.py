import pytest
from wagtail.core.models import Page

from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def root_page():
    """
    On start Wagtail provides one page with ID=1 and it's called "Root page"
    """
    page_content_type, _ = ContentType.objects.get_or_create(
        model='page',
        app_label='wagtailcore'
    )
    root, _ = Page.objects.get_or_create(
        slug='root',
        defaults=dict(
            title='Root',
            content_type=page_content_type,
            path='0001',
            depth=1,
            numchild=1,
            url_path='/',
        )
    )
    return root
