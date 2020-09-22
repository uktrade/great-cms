from unittest import mock

import pytest

from django.template import Context, Template
from datetime import timedelta

from core.templatetags.personalised_blocks import render_video_block
from core.templatetags.video_tags import render_video


def test_render_personalised_video_block_tag():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}]
    )
    block = dict(
        width=20,
        height=20,
        video=video_mock
    )
    html = render_video_block(block)

    assert '<video width="20" height="20" controls>' in html
    assert '<source src="/media/foo.mp4" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_general_render_video_tag():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}],
        duration=120,
    )
    block = dict(
        video=video_mock
    )
    html = render_video(block)

    assert '<video controls data-v-duration="120">' in html
    assert '<source src="/media/foo.mp4" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_empty_block_render_video_tag():

    block = dict()
    html = render_video(block)
    assert '' in html


@pytest.mark.django_db
def test_format_timedelta_filter(user, rf, domestic_site):
    cases = [
        {'value': timedelta(seconds=0), 'result': '0 min:0 min'},
        {'value': timedelta(seconds=25), 'result': '1 min:1 min'},
        {'value': timedelta(seconds=70), 'result': '2 min:2 mins'},
        {'value': timedelta(seconds=4500), 'result': '1 hour 15 min:1 hour 15 mins'},
        {'value': timedelta(seconds=7200), 'result': '2 hour:2 hours'},
        {'value': None, 'result': ':'}
    ]

    template = Template(
        '{% load format_timedelta from content_tags %}'
        '{{ delta|format_timedelta }}:{{ delta|format_timedelta:True }}'
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


@pytest.mark.django_db
def test_tojson(user, rf, domestic_site):

    template = Template(
        '{% load to_json %}'
        '{{ data|to_json }}'
    )

    html = template.render(Context({'data': {'thing1': 'one', 'thing2': 'two'}}))
    assert html == '{"thing1": "one", "thing2": "two"}'


@pytest.mark.django_db
def test_set(user, rf, domestic_site):

    template = Template(
        '{% load set %}'
        "{% set 'my_variable' 1234 %}"
        '{{ my_variable }}'
    )

    html = template.render(Context({}))
    assert html == '1234'


@pytest.mark.django_db
def test_get_item_filter(user, rf, domestic_site):
    cases = [
        {'lesson_details': {'my-lesson': {'topic_name': 'my topic'}}, 'result': 'my topic'},
        {'lesson_details': {'myLesson2': {'topic_name': 'my topic'}}, 'result': ''},
        {'lesson_details': '', 'result': ''},
    ]

    template = Template(
        '{% load object_tags %}'
        '{{ lesson_details|get_item:\"my-lesson\"|get_item:\"topic_name\" }}'
    )

    for case in cases:
        html = template.render(Context({'lesson_details': case.get('lesson_details')}))
        assert html == case.get('result')
