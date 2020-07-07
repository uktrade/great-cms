import pytest

from django.template import Context, Template
from datetime import timedelta


@pytest.mark.django_db
def test_format_timedelta_filter(user, rf, domestic_site):
    cases = [
        {'value': timedelta(seconds=0), 'result': '0 min'},
        {'value': timedelta(seconds=25), 'result': '1 min'},
        {'value': timedelta(seconds=70), 'result': '2 mins'},
        {'value': timedelta(seconds=4500), 'result': '1 hour 15 mins'},
        {'value': timedelta(seconds=7200), 'result': '2 hours'},
        {'value': None, 'result': ''}
    ]

    template = Template(
        '{% load format_timedelta from content_tags %}'
        '{{ delta|format_timedelta }}'
    )
    for case in cases:
        context = Context({'delta': case.get('value')})
        html = template.render(context)
        assert html == case.get('result')


@pytest.mark.django_db
def test_pluralize(user, rf, domestic_site):
    cases = [
        {'value': 0, 'result': 's'},
        {'value': 1, 'result': ''},
        {'value': 2, 'result': 's'},
    ]

    template = Template(
        '{% load pluralize from content_tags %}'
        '{% pluralize value %}'
    )
    for case in cases:
        html = template.render(Context({'value': case.get('value')}))
        assert html == case.get('result')
