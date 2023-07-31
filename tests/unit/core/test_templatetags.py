import datetime
from datetime import timedelta
from html import escape
from unittest import mock
from urllib.parse import quote, quote_plus

import pytest
from django.conf import settings
from django.template import Context, Template
from django.urls import reverse

from core.models import CuratedListPage, DetailPage, LessonPlaceholderPage, TopicPage
from core.templatetags.content_tags import (
    get_backlinked_url,
    get_category_title_for_lesson,
    get_lesson_progress_for_topic,
    get_link_blocks,
    get_template_translation_enabled,
    get_text_blocks,
    get_topic_title_for_lesson,
    highlighted_text,
    is_lesson_page,
    is_placeholder_page,
    make_bold,
    str_to_datetime,
)
from core.templatetags.object_tags import get_item
from core.templatetags.progress_bar import progress_bar
from core.templatetags.url_map import path_match
from core.templatetags.url_tags import get_intended_destination
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
        subtitles=[],
    )
    block = dict(video=video_mock)
    html = render_video(block)

    assert (
        # Whitespace in this string is important for matching output
        '<video preload="metadata" controls controlsList="nodownload"\n'
        '            poster="https://example.com/thumb.png" data-v-duration="120">'
    ) in html
    assert '<source src="/media/foo.mp4#t=0.1" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_render_video_tag__without_thumbnail():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}],
        duration=120,
        thumbnail=None,
        subtitles=[],
    )
    block = dict(video=video_mock)
    html = render_video(block)
    # Whitespace in this string is important for matching output
    assert '<video preload="metadata" controls controlsList="nodownload"\n            data-v-duration="120">' in html
    assert '<source src="/media/foo.mp4#t=0.1" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html


def test_render_video_tag__with_subtitles():
    video_mock = mock.Mock(
        sources=[{'src': '/media/foo.mp4', 'type': 'video/mp4'}],
        duration=120,
        thumbnail=None,
        subtitles=[
            {
                'srclang': 'en',
                'label': 'English',
                'url': reverse('core:subtitles-serve', args=[123, 'en']),
                'default': False,
            },
            {
                'srclang': 'tt',
                'label': 'TestLang',
                'url': reverse('core:subtitles-serve', args=[123, 'tt']),
                'default': True,
            },
        ],
    )
    block = dict(video=video_mock)
    html = render_video(block)
    # Whitespace in this string is important for matching output
    assert '<video preload="metadata" controls controlsList="nodownload"\n            data-v-duration="120">' in html
    assert '<source src="/media/foo.mp4#t=0.1" type="video/mp4">' in html
    assert 'Your browser does not support the video tag.' in html
    assert '<track label="TestLang" kind="subtitles" srclang="tt" src="/subtitles/123/tt/content.vtt" default>' in html
    assert '<track label="English" kind="subtitles" srclang="en" src="/subtitles/123/en/content.vtt">' in html


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


def test_str_to_datetime():
    assert str_to_datetime('2021-07-22T13:40:49.207335Z') == datetime.datetime(
        2021, 7, 22, 13, 40, 49, 207335, tzinfo=datetime.timezone.utc
    )
    assert str_to_datetime('2022-08-03T00:00:00.000Z') == datetime.datetime(
        2022, 8, 3, 0, 0, 0, 0, tzinfo=datetime.timezone.utc
    )


@pytest.mark.parametrize('month,expected', ((1, 'January'), (6, 'June'), (12, 'December'), (None, '')))
@pytest.mark.django_db
def test_month_name(user, rf, domestic_site, month, expected):
    template = Template('{% load month_name from content_tags %}{{ month|month_name }}')
    assert template.render(Context({'month': month})) == expected


@pytest.mark.parametrize(
    'val1,val2,expected',
    (
        ('one', 'two', 'onetwo'),
        ('', 'two', 'two'),
        (12, 'two', '12two'),
        ('one', 234, 'one234'),
    ),
)
@pytest.mark.django_db
def test_concat(user, rf, domestic_site, val1, val2, expected):
    template = Template('{% load concat from content_tags %}{{ val1|concat:val2 }}')
    assert template.render(Context({'val1': val1, 'val2': val2})) == expected


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
def test_get_topic_and_category_title_for_lesson(domestic_homepage, domestic_site):
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

    # and the categories
    assert get_category_title_for_lesson(detail_page_1) == 'Module 1'
    assert get_category_title_for_lesson(detail_page_2) == 'Module 1'
    assert get_category_title_for_lesson(detail_page_3) == 'Module 1'
    assert get_category_title_for_lesson(detail_page_4) == 'Module 2'


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
def test_get_lesson_progress_for_topic(
    lesson_completion_data_spec,
    lesson_and_placeholder_spec_data,
    expected,
    en_locale,
):
    topic_page = factories.TopicPageFactory(title='test-topic')

    _build_lesson_and_placeholder_spec(lesson_and_placeholder_spec_data, topic_page)

    lesson_completion_data = _build_lesson_completion_data(lesson_completion_data_spec, topic_page)

    # Uncomment these lines to help if you're refactoring/extending these tests
    # print('\nlesson_and_placeholder_spec_data', lesson_and_placeholder_spec_data)
    # print('lesson_completion_data', lesson_completion_data)
    # print('actual page IDs', DetailPage.objects.all().values_list('id', flat=True))

    assert get_lesson_progress_for_topic(lesson_completion_data, topic_page.id) == expected


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.parametrize(
    'path_info, expected_destination, default_destination',
    (
        ('/path/in/', '/dashboard/', None),
        ('/path/in/?next=/path/to/page/', '/path/to/page/', None),
        ('/path/in/?next=', '/dashboard/', None),
        ('/path/in/?next=/login/', '/dashboard/', None),
        ('/path/in/?next=/signup/', '/dashboard/', None),
        ('/path/in/', '/foo/', '/foo/'),
        ('/path/in/?next=/path/to/?token=foo-bar', '/path/to/?token=foo-bar', None),
        ('/path/in/?next=/path/to/?next=/foo/bar/', '/path/to/?next=/foo/bar/', None),
        ('/path/in/?next=https://example.com/foo/bar/', '/dashboard/', None),
        ('/path/in/?next=test', '/dashboard/', None),
        ('/path/in/?next=http://testserver/path/to', 'http://testserver/path/to', None),
        ('/path/in/?next=https://testserver/path/to', 'https://testserver/path/to', None),
        ('/path/in/?next=bad_https://testserver/path/to', '/dashboard/', None),
        ('/path/in/?next=//badserver/path/to', '/dashboard/', None),
        ('/path/in/?next=//testserver/path/to', '//testserver/path/to', None),
        (quote('/path/in/?next=https://example.com/foo/bar/'), '/dashboard/', None),
        (quote_plus('/path/in/?next=https://example.com/foo/bar/'), '/dashboard/', None),
        (escape('/path/in/?next=https://example.com/foo/bar/'), '/dashboard/', None),
    ),
    ids=[
        'simple path - no onward dest',
        'simple path with next param',
        'next param is skip-list path: root',
        'next param is skip-list path: login',
        'next param is skip-list path: signup',
        'custom default destination',
        'next param path with querystring allowed',
        'next param path with duplicated "next" querystring allowed',
        'next param path with querysting with hints of full url',
        'next param is non-relative path',
        'next param is absolute path with matching domain',
        'next param is absolute path with https matching domain',
        'next param has absolute path with matching domain not at start',
        'next param has double-slash absolute path',
        'next param has double-slash absolute path with matching domain',
        'quoted path with querysting with hints of full url',
        'plus-quoted path with querysting with hints of full url',
        'entity-escaped path with querysting with hints of full url',
    ],
)
def test_get_intended_destination(rf, path_info, expected_destination, default_destination):
    request = rf.get(path_info)
    if default_destination is not None:
        assert get_intended_destination(request, default_destination) == expected_destination
    else:
        assert get_intended_destination(request) == expected_destination


@pytest.mark.django_db
def test_friendly_number():
    cases = [
        {'value': 1110000, 'result': '1.11 million'},
        {'value': 111000, 'result': '111.00 thousand'},
        {'value': 11100, 'result': '11.10 thousand'},
    ]

    template = Template('{% load friendly_number from content_tags %}{{ delta|friendly_number }}')

    for case in cases:
        context = Context({'delta': case.get('value')})
        html = template.render(context)
        assert html == case.get('result')


@pytest.mark.django_db
def test_multiply_by_exponent():
    cases = [
        {'value': 13000, 'result': '13000000'},
        {'value': 1, 'result': '1000'},
        {'value': 130000, 'result': '130000000'},
    ]

    template = Template('{% load multiply_by_exponent from content_tags %}{{ delta|multiply_by_exponent }}')

    for case in cases:
        context = Context({'delta': case.get('value')})
        html = template.render(context)
        assert html == case.get('result')


@pytest.mark.parametrize(
    'number, unit, precision, expected',
    (
        (12345.1, '', 1, '12345.1'),
        (12345.1, 'invalid-unit', 1, '12345.1'),
        (12345.1, 'invalid-unit', 0, '12345'),
        (1230, 'thousand', 1, '1.2'),
        (1230000, 'thousand', 0, '1230'),
        (1230000, 'million', 0, '1'),
        (1230000, 'million', 1, '1.2'),
        (1290000, 'million', 1, '1.3'),
        (80000000, 'billion', 1, '0.1'),
        (8509000000, 'billion', 1, '8.5'),
        (8509000000, 'billion', 2, '8.51'),
        (8009000000, 'billion', 1, '8.0'),
        (8009000000, 'billion', 2, '8.01'),
    ),
)
def test_round_to_unit(number, unit, precision, expected):
    template = Template('{% load round_to_unit from content_tags %}{% round_to_unit number unit precision %}')

    context = Context({'number': number, 'unit': unit, 'precision': precision})
    html = template.render(context)
    assert html == expected


@pytest.mark.parametrize(
    'number, unit, expected',
    ((1234, 'thousand', '1.2'), (1000, 'thousand', '1.0')),
)
def test_round_to_unit_default_precision(number, unit, expected):
    template = Template('{% load round_to_unit from content_tags %}{% round_to_unit number unit %}')

    context = Context({'number': number, 'unit': unit})
    html = template.render(context)
    assert html == expected


@pytest.mark.parametrize(
    'resolution, period, year, capitalise, expected',
    (
        ('month', 3, 2022, False, 'twelve months to the end of March 2022'),
        ('month', 12, 2021, False, 'twelve months to the end of December 2021'),
        ('month', 0, 2022, False, ''),
        ('quarter', 3, 2022, False, 'four quarters to the end of Q3 2022'),
        ('month', 0, 2022, False, ''),
        ('month', 3, 2022, True, 'Twelve months to the end of March 2022'),
        ('quarter', 3, 2022, True, 'Four quarters to the end of Q3 2022'),
    ),
)
def test_reference_period(resolution, period, year, capitalise, expected):
    template = Template('{% load reference_period from content_tags %}{% reference_period data capitalise %}')

    context = Context({'data': {'resolution': resolution, 'period': period, 'year': year}, 'capitalise': capitalise})
    html = template.render(context)
    assert html == expected


@pytest.mark.parametrize(
    'input_html, expected_html',
    (
        ('<h1>content</h1>', '<h1 class="govuk-heading-xl">content</h1>'),
        ('<h2>content</h2>', '<h2 class="govuk-heading-l">content</h2>'),
        ('<h3>content</h3>', '<h3 class="govuk-heading-m great-font-size-28">content</h3>'),
        ('<h4>content</h4>', '<h4 class="govuk-heading-s">content</h4>'),
        ('<h5>content</h5>', '<h5 class="govuk-heading-xs">content</h5>'),
        ('<h6>content</h6>', '<h6 class="govuk-heading-xs">content</h6>'),
        ('<ul>content</ul>', '<ul class="govuk-list govuk-list--bullet">content</ul>'),
        ('<ol>content</ul>', '<ol class="govuk-list govuk-list--number">content</ol>'),
        ('<p>content</p>', '<p class="govuk-body">content</p>'),
        ('<a>content</a>', '<a class="govuk-link">content</a>'),
        ('<div class="form-group other-class">test</div>', '<div class="govuk-form-group other-class">test</div>'),
        ('<div class="form-group-error">test</div>', '<div class="govuk-form-group-error">test</div>'),
        ('<input class="form-control"/>', '<input class="govuk-form-control"/>'),
        ('<label class="form-label">test</label>', '<label class="govuk-form-label">test</label>'),
        (
            '<iframe src="" title=""></iframe>',
            '<div class="great-video-embed-16-9"><iframe src="" title=""></iframe></div>',
        ),
    ),
)
def test_add_govuk_classes(input_html, expected_html):
    template = Template('{% load add_govuk_classes from content_tags %}' '{{ html|add_govuk_classes }}')
    context = Context({'html': input_html})
    html = template.render(context)
    assert html == expected_html


@pytest.mark.parametrize(
    'input, expected_instances',
    (
        ([factories.BlockFactory('link_block')], 1),
        ([factories.BlockFactory('another_block')], 0),
        ([factories.BlockFactory('link_block'), factories.BlockFactory('another_block')], 1),
    ),
)
def test_get_link_blocks(input, expected_instances):
    assert len(get_link_blocks(input)) == expected_instances


@pytest.mark.parametrize(
    'input, expected_instances',
    (
        ([factories.BlockFactory('text')], 1),
        ([factories.BlockFactory('another_block')], 0),
        ([factories.BlockFactory('text'), factories.BlockFactory('another_block')], 1),
    ),
)
def test_get_text_blocks(input, expected_instances):
    assert len(get_text_blocks(input)) == expected_instances


def test_get_template_translation_enabled_matches_settings():
    assert get_template_translation_enabled() == settings.FEATURE_MICROSITE_ENABLE_TEMPLATE_TRANSLATION


def test_replace_emphasis_tags():
    template = Template('{% load replace_emphasis_tags from content_tags %}' '{{ content|replace_emphasis_tags }}')

    # Test case 1: <i> tag inside <p class="govuk-body">
    content = '<p class="govuk-body"><i>Some content</i></p>'
    expected_output = '<p class="govuk-body"><em>Some content</em></p>'
    context = Context({'content': content})
    rendered = template.render(context)
    assert rendered.strip() == expected_output

    # Test case 2: <i> tag inside <p> without class="govuk-body"
    content = '<p><i>Some content</i></p>'
    expected_output = '<p><i>Some content</i></p>'
    context = Context({'content': content})
    rendered = template.render(context)
    assert rendered.strip() == expected_output

    # Test case 3: No <p> tag
    content = '<i>Some content</i>'
    expected_output = '<i>Some content</i>'
    context = Context({'content': content})
    rendered = template.render(context)
    assert rendered.strip() == expected_output

    # Test case 4: Replace <b> inside <i>  tag
    content = '<p class="govuk-body"><b><i>Some content</i></b></p>'
    expected_output = '<p class="govuk-body"><strong><em>Some content</em></strong></p>'
    context = Context({'content': content})
    rendered = template.render(context)
    assert rendered.strip() == expected_output


def test_make_bold_tag():
    text = 'Hello'
    expected_output = make_bold(text)
    assert expected_output == '<span class="govuk-!-font-weight-bold">Hello</span>'


def test_highlighted_text():
    result = highlighted_text(['a', 'b'])
    expected_output = '<span class="great-highlighted-text">a, </span><span class="great-highlighted-text">b</span>'
    assert result == expected_output
