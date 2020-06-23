import pytest

from django.template import Context, Template

from tests.unit.core.factories import DetailPageFactory


@pytest.mark.django_db
@pytest.mark.parametrize('page_count,expected', (
    (1, '1 min'),
    (2, '2 mins'),
    (10, '7 mins'),
    (20, '13 mins'),
    (50, '32 mins'),
    (100, '1 hour 4 mins'),
    (200, '2 hours 7 mins'),
))
def test_read_time(page_count, expected, user, rf, domestic_site):
    request = rf.get('/')
    request.user = user

    template = Template(
        '{% load read_time from content_tags %}'
        '{% read_time pages %}'
    )

    pages = (
        DetailPageFactory(
            template='learn/detail_page.html',
            body='hello',
            parent=domestic_site.root_page,
        ) for count in range(page_count)
    )
    context = Context({'pages': pages, 'request': request})
    html = template.render(context)

    assert html == expected
