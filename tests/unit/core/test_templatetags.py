import pytest

from django.template import Context, Template

from tests.unit.core.factories import DetailPageFactory


@pytest.mark.django_db
def test_read_time(user, rf, domestic_site):
    request = rf.get('/')
    request.user = user

    template = Template(
        '{% load read_time from content_tags %}'
        '{% read_time page %}'
    )

    page = DetailPageFactory(
        template='learn/detail_page.html',
        body='hello',
        parent=domestic_site.root_page,
    )
    context = Context({'page': page, 'request': request})
    html = template.render(context)

    assert html == '1 min'
