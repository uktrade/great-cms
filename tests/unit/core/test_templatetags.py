from datetime import timedelta
from unittest import mock

import pytest
from django.template import Context, Template

from core.models import CuratedListPage, DetailPage, LessonPlaceholderPage, TopicPage
from core.templatetags.content_tags import (
    get_backlinked_url,
    get_lesson_progress_for_topic,
    get_topic_title_for_lesson,
    is_lesson_page,
    is_placeholder_page,
)
from core.templatetags.object_tags import get_item
from core.templatetags.progress_bar import progress_bar
from core.templatetags.url_map import path_match
from core.templatetags.video_tags import render_video
from tests.unit.core import factories


def test_render_video_tag__with_thumbnail():
    mock_thumbnail = mock.Mock(name='thumbnail')
    mock_thumbnail.url = 'https://example.com/thumb.png'

    video_mock = mock.Mock(
        name='video_mock',
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}],
        duration=120,
        thumbnail=mock_thumbnail,
    )
    block = dict(video=video_mock)
    html = render_video(block)

    assert '<video controls poster="https://example.com/thumb.png" data-v-duration="120">' in html
    assert '<source src="/media/foo.mp4" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_render_video_tag__without_thumbnail():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}],
        duration=120,
        thumbnail=None,
    )
    block = dict(video=video_mock)
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
        {'value': None, 'result': ':'},
    ]

    template = Template(
        '{% load format_timedelta from content_tags %}{{ delta|format_timedelta }}:{{ delta|format_timedelta:True }}'
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

    template = Template('{% load pluralize from content_tags %}{% pluralize value %}')
    for case in cases:
        html = template.render(Context({'value': case.get('value')}))
        assert html == case.get('result')


@pytest.mark.django_db
def test_tojson(user, rf, domestic_site):

    template = Template('{% load to_json %}{{ data|to_json }}')

    html = template.render(Context({'data': {'thing1': 'one', 'thing2': 'two'}}))
    assert html == '{"thing1": "one", "thing2": "two"}'


@pytest.mark.django_db
def test_set(user, rf, domestic_site):

    template = Template("{% load set %}{% set 'my_variable' 1234 %}{{ my_variable }}")

    html = template.render(Context({}))
    assert html == '1234'


@pytest.mark.django_db
def test_get_item_filter(user, rf, domestic_site):
    cases = [
        {'lesson_details': {'my-lesson': {'topic_name': 'my topic'}}, 'result': 'my topic'},
        {'lesson_details': {'myLesson2': {'topic_name': 'my topic'}}, 'result': ''},
        {'lesson_details': '', 'result': ''},
    ]

    template = Template('{% load object_tags %}{{ lesson_details|get_item:\"my-lesson\"|get_item:\"topic_name\" }}')

    for case in cases:
        html = template.render(Context({'lesson_details': case.get('lesson_details')}))
        assert html == case.get('result')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'request_path,outbound_url,expected_backlinked_url',
    (
        (
            '/example/export-plan/path/',
            '/test/outbound/path/',
            '/test/outbound/path/?return-link=%2Fexample%2Fexport-plan%2Fpath%2F',
        ),
        (
            '/example/export-plan/path/?foo=bar',
            '/test/outbound/path/',
            '/test/outbound/path/?return-link=%2Fexample%2Fexport-plan%2Fpath%2F%3Ffoo%3Dbar',
        ),
        (
            '/example/export-plan/path/',
            'https://example.com/test/outbound/path/',
            'https://example.com/test/outbound/path/?return-link=%2Fexample%2Fexport-plan%2Fpath%2F',
        ),
        (
            '/example/export-plan/path/?foo=bar',
            'https://example.com/test/outbound/path/',
            ('https://example.com/test/outbound/path/?return-link=%2Fexample%2Fexport-plan%2Fpath%2F%3Ffoo%3Dbar'),
        ),
        (
            '/example/export-plan/path/?foo=bar',
            '/test/outbound/path/?bam=baz',
            ('/test/outbound/path/?bam=baz&return-link=%2Fexample%2Fexport-plan%2Fpath%2F%3Ffoo%3Dbar'),
        ),
        (
            '/example/export-plan/path/?foo=bar',
            'https://example.com/test/outbound/path/?bam=baz',
            (
                'https://example.com/test/outbound/path/'
                '?bam=baz&return-link=%2Fexample%2Fexport-plan%2Fpath%2F%3Ffoo%3Dbar'
            ),
        ),
    ),
    ids=[
        '1. Outbound path with NO existing querystring for the source/request path',
        '2. Outbound path with an existing querystring for the source/request path',
        '3. Full outbound URL with NO existing querystring for the source/request path',
        '4. Full outbound URL with existing querystring for the source/request path',
        '5. Both source/request and outbound URLs feature querystrings',
        '5. Both source/request and outbound URLs feature querystrings; outbound is a full URL',
    ],
)
def test_get_backlinked_url(rf, request_path, outbound_url, expected_backlinked_url):
    context = {'request': rf.get(request_path)}
    assert get_backlinked_url(context, outbound_url) == expected_backlinked_url


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path, expected',
    (
        ('/example/', True),
        ('/example/morepath/', True),
        ('/export-plan/example/', False),
        ('', False),
    ),
    ids=['match base path', 'match extended path', 'non-match', 'empty path'],
)
def test_path_match(rf, path, expected):
    context = {'request': rf.get(path)}
    match = path_match(context, '^\\/example\\/')
    assert bool(match) == expected


def test_path_match_no_path(rf):
    context = {}
    match = path_match(context, '')
    assert match is None


@pytest.mark.django_db
def test_push(user, rf, domestic_site):

    template = Template(
        '{% load set %}'
        "{% push 'my_variable' 'item1' %}"
        "{% push 'my_variable' 'item2' %}"
        'one:{{ my_variable.0 }} '
        'two:{{ store.my_variable.1 }}'
    )

    html = template.render(Context({}))
    assert html == 'one:item1 two:item2'


@pytest.mark.parametrize(
    'data,key,expected',
    (
        ({'foo': 'bar'}, 'foo', 'bar'),
        ({'foo': 'bar'}, 'bam', None),
        ({1: 'bar'}, 1, 'bar'),
        ({'1': 'bar'}, 1, None),
        ({1: 'bar'}, '1', None),
        ('a string has no get attr', 'foo', ''),
        ({'foo': 'bar'}, 'FOO', 'bar'),
    ),
)
def test_get_item(data, key, expected):
    assert get_item(data, key) == expected


@pytest.mark.parametrize(
    'total,complete,percentage',
    (
        (10, 0, '0%'),
        (10, 5, '50%'),
        (10, 10, '100%'),
        (0, 0, '0%'),
    ),
)
def test_progress_bar(total, complete, percentage):
    html = progress_bar(total, complete)
    check = f'style="width:{percentage}"'
    assert html.find(check) > 0


@pytest.mark.django_db
def test_get_topic_title_for_lesson(domestic_homepage, domestic_site):

    # Lots of setup, alas

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )

    topic_page_1 = factories.TopicPageFactory(title='Topic 1', parent=module_1)
    topic_page_2 = factories.TopicPageFactory(title='Topic 2', parent=module_1)
    topic_page_3 = factories.TopicPageFactory(title='Topic 3', parent=module_2)

    # Topic One children
    detail_page_1 = factories.DetailPageFactory(slug='detail-page-1-1', parent=topic_page_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder One', parent=topic_page_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-1-2', parent=topic_page_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder Two', parent=topic_page_1)

    # Topic Two children
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-1-3', parent=topic_page_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Two', parent=topic_page_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Two', parent=topic_page_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Three', parent=topic_page_2)

    # Topic Three children
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder One', parent=topic_page_3)
    detail_page_4 = factories.DetailPageFactory(slug='detail-page-4-2', parent=topic_page_3)
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder Two', parent=topic_page_3)

    # Finally, to the test:
    assert get_topic_title_for_lesson(detail_page_1) == 'Topic 1'
    assert get_topic_title_for_lesson(detail_page_2) == 'Topic 1'
    assert get_topic_title_for_lesson(detail_page_3) == 'Topic 2'
    assert get_topic_title_for_lesson(detail_page_4) == 'Topic 3'


def _build_lesson_and_placeholder_spec(data, topic_page):
    for lesson_id in range(data['lessons_to_create']):
        factories.DetailPageFactory.create(parent=topic_page, slug=f'lesson-{lesson_id}', title=f'Lesson {lesson_id}')

    for placeholder_title in data['placeholders']:
        factories.LessonPlaceholderPageFactory.create(parent=topic_page, title=placeholder_title)


def _build_lesson_completion_data(spec, topic_page):  # noqa C901  # is less complex than it looks
    if spec == 'all':
        return set(DetailPage.objects.all().values_list('id', flat=True))

    elif spec == 'none':
        return set()

    elif spec == 'subset':
        return set(DetailPage.objects.all().values_list('id', flat=True)[:1])

    elif spec == 'different':
        retval = set()
        for lesson_id in range(100, 102):
            factories.DetailPageFactory.create(
                parent=topic_page, slug=f'lesson-{lesson_id}', title=f'Lesson {lesson_id}'
            )
            retval.add(lesson_id)
        return retval

    elif spec == 'partial_overlap':
        # get a real page to include in completion stats
        retval = set(DetailPage.objects.all().values_list('id', flat=True)[:1])

        # and two uknown pages to include in completion stats
        for lesson_id in range(100, 101):
            factories.DetailPageFactory.create(
                parent=topic_page, slug=f'lesson-{lesson_id}', title=f'Lesson {lesson_id}'
            )
            retval.add(lesson_id)
        return retval

    assert False, 'Misconfigured test data'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lesson_completion_data_spec,lesson_and_placeholder_spec_data,expected',
    (
        ('subset', {'lessons_to_create': 2, 'placeholders': []}, {'lessons_completed': 1, 'lessons_available': 2}),
        ('all', {'lessons_to_create': 4, 'placeholders': []}, {'lessons_completed': 4, 'lessons_available': 4}),
        ('none', {'lessons_to_create': 4, 'placeholders': []}, {'lessons_completed': 0, 'lessons_available': 4}),
        (
            'subset',  # eg {3},
            {'lessons_to_create': 2, 'placeholders': ['one']},
            {'lessons_completed': 1, 'lessons_available': 2},
        ),
        (
            'all',
            {'lessons_to_create': 4, 'placeholders': ['one', 'two']},
            {'lessons_completed': 4, 'lessons_available': 4},
        ),
        (
            'none',
            {'lessons_to_create': 4, 'placeholders': ['one', 'two', 'three']},
            {'lessons_completed': 0, 'lessons_available': 4},
        ),
        ('none', {'lessons_to_create': 0, 'placeholders': []}, {'lessons_completed': 0, 'lessons_available': 0}),
        ('different', {'lessons_to_create': 0, 'placeholders': []}, {}),
        ('partial_overlap', {'lessons_to_create': 3, 'placeholders': []}, {}),
    ),
    ids=(
        'two lessons, one completed',
        'four lessons, all completed',
        'four lessons, none completed',
        'two lessons, placeholders, one completed lesson',
        'four lessons, placeholders, all completed',
        'four lessons, placeholders, none completed',
        'no lessons, none completed',
        ('bad data: two lessons completed but not mentioned in lesson_and_placeholder_spec'),
        (
            'bad data: two lessons completed but not a '
            'subset of those in lesson_and_placeholder_spec - partial overlap'
        ),
    ),
)
def test_get_lesson_progress_for_topic(lesson_completion_data_spec, lesson_and_placeholder_spec_data, expected):
    topic_page = factories.TopicPageFactory(title='test-topic')

    _build_lesson_and_placeholder_spec(lesson_and_placeholder_spec_data, topic_page)

    lesson_completion_data = _build_lesson_completion_data(lesson_completion_data_spec, topic_page)

    # Uncomment these lines to help if you're refactoring/extending these tests
    # print('\nlesson_and_placeholder_spec_data', lesson_and_placeholder_spec_data)
    # print('lesson_completion_data', lesson_completion_data)
    # print('actual page IDs', DetailPage.objects.all().values_list('id', flat=True))

    assert get_lesson_progress_for_topic(lesson_completion_data, topic_page.id) == expected


@pytest.mark.parametrize(
    'klass,expected',
    (
        (DetailPage, True),
        (LessonPlaceholderPage, False),
        (CuratedListPage, False),
        (TopicPage, False),
    ),
)
def test_is_lesson_page(klass, expected):
    assert is_lesson_page(klass()) == expected


@pytest.mark.parametrize(
    'klass,expected',
    (
        (DetailPage, False),
        (LessonPlaceholderPage, True),
        (CuratedListPage, False),
        (TopicPage, False),
    ),
)
def test_is_placeholder_page(klass, expected):
    assert is_placeholder_page(klass()) == expected
