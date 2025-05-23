import datetime
from unittest import mock

import pytest
from django.conf import settings
from django.core.paginator import Paginator
from django.http import QueryDict
from django.template import Context, Template
from django.test import override_settings
from django.utils import timezone

from core.templatetags.content_tags import convert_anchor_identifier_a_to_span
from domestic.templatetags.component_tags import (
    append_past_year_seperator,
    get_market_widget_data,
    get_meta_description,
    get_pagination_url,
    get_projected_or_actual,
    industry_accordion_case_study_is_viable,
    industry_accordion_is_viable,
    pagination_obj_range_lower_limit,
    pagination_obj_range_upper_limit,
    persist_language,
    replace_hyphens,
    replace_underscores,
)
from tests.unit.export_academy.factories import EventFactory


def test_static_absolute(rf):
    template = Template('{% load static_absolute from component_tags %}' '{% static_absolute "images/favicon.ico" %}')

    context = Context({'request': rf.get('/')})
    html = template.render(context)

    assert html == ('http://testserver/static/images/favicon.ico')


def test_breadcrumbs_simple(rf):
    # TODO: add exhaustive testing of this tag

    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs %}'
        '<a href="/path/to/">EXAMPLE LINK ONE</a>'
        '<a href="/path/to/something">EXAMPLE LINK TWO</a>'
        '{% endbreadcrumbs %}'
        '</div>'
        '{% endblock %}'
    )

    context = Context({'request': rf.get('/')})
    html = template.render(context)

    assert html == (
        '<div class="container">\n'
        '<nav aria-label="Breadcrumb" class="breadcrumbs">\n'
        '<ol>\n'
        '<li><a href="/path/to/" tabindex="-1">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something" tabindex="-1">EXAMPLE LINK TWO</a></li>'
        '</ol>\n'
        '</nav>\n</div>'
    )


def test_breadcrumbs_simple__root_url_override(rf):
    #  Tests our ability to override the URL for the hard-coded root breadcrumb
    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs %}'
        '<a href="{{BREADCRUMBS_ROOT_URL}}">great.gov.uk</a>'
        '<a href="/path/to/">EXAMPLE LINK ONE</a>'
        '<a href="/path/to/something">EXAMPLE LINK TWO</a>'
        '{% endbreadcrumbs %}'
        '</div>'
        '{% endblock %}'
    )

    # Check the default value
    assert settings.BREADCRUMBS_ROOT_URL == 'https://great.gov.uk/'
    context = Context(
        {
            'request': rf.get('/'),
            'BREADCRUMBS_ROOT_URL': settings.BREADCRUMBS_ROOT_URL,  # set via context processor, normally
        }
    )
    html = template.render(context)

    assert html == (
        '<div class="container">\n'
        '<nav aria-label="Breadcrumb" class="breadcrumbs">\n'
        '<ol>\n'
        '<li><a href="https://great.gov.uk/" tabindex="-1">great.gov.uk</a></li>'
        '<li><a href="/path/to/" tabindex="-1">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something" tabindex="-1">EXAMPLE LINK TWO</a></li>'
        '</ol>\n'
        '</nav>\n</div>'
    )

    # check a different setting gets a different result
    with override_settings(BREADCRUMBS_ROOT_URL='http://test.example.com/'):
        assert settings.BREADCRUMBS_ROOT_URL == 'http://test.example.com/'
        context = Context(
            {
                'request': rf.get('/'),
                'BREADCRUMBS_ROOT_URL': settings.BREADCRUMBS_ROOT_URL,  # set via context processor, normally
            }
        )
        html = template.render(context)

    assert html == (
        '<div class="container">\n'
        '<nav aria-label="Breadcrumb" class="breadcrumbs">\n'
        '<ol>\n'
        '<li><a href="http://test.example.com/" tabindex="-1">great.gov.uk</a></li>'
        '<li><a href="/path/to/" tabindex="-1">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something" tabindex="-1">EXAMPLE LINK TWO</a></li>'
        '</ol>\n'
        '</nav>\n</div>'
    )


def test_breadcrumb_missing_href(rf):
    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs %}'
        '<a>EXAMPLE LINK ONE</a>'  # MISSING THE HREF
        '<a href="/path/to/something">EXAMPLE LINK TWO</a>'
        '{% endbreadcrumbs %}'
        '</div>'
        '{% endblock %}'
    )

    context = Context({'request': rf.get('/')})
    with pytest.raises(ValueError) as ctx:
        template.render(context)
        assert ctx.message == 'Missing href in breadcrumb'


def test_breadcrumb_no_links(rf):
    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs %}'
        '{% endbreadcrumbs %}'
        '</div>'
        '{% endblock %}'
    )

    context = Context({'request': rf.get('/')})
    with pytest.raises(ValueError) as ctx:
        template.render(context)
        assert ctx.message == 'Please specify some links'


def test_ga360_data_with_no_optional_parameters():
    template = Template(
        '{% load ga360_data from component_tags %}'
        '{% ga360_data "a" %}'
        '<div>'
        '    <a href="example.com">Click Me</a>'
        '</div>'
        '{% end_ga360_data %}'
    )

    rendered_html = template.render(Context())

    expected_html = '<div>' ' <a href="example.com">Click Me</a>' '</div>'
    assert rendered_html == expected_html


def test_ga360_data_with_all_optional_parameters():
    template = Template(
        '{% load ga360_data from component_tags %}'
        '{% ga360_data "a" action="link" type="CTA" element="pageSection" value="Click Me" include_form_data="True" %}'  # noqa
        '<div>'
        '    <a href="example.com">Click Me</a>'
        '</div>'
        '{% end_ga360_data %}'
    )

    rendered_html = template.render(Context())

    expected_html = (
        '<div>'
        ' <a data-ga-action="link" data-ga-element="pageSection" '
        'data-ga-include-form-data="True" '
        'data-ga-type="CTA" data-ga-value="Click Me" '
        'href="example.com">Click Me</a>'
        '</div>'
    )
    assert rendered_html == expected_html


@pytest.mark.parametrize(
    'data,expected',
    (
        (
            {
                'title': 'test title',
                'teaser': 'test teaser',
                'subsections': [
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ],
            },
            True,
        ),
        (
            {
                # 'title': 'test title',
                'teaser': 'test teaser',
                'subsections': [
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ],
            },
            False,
        ),
        (
            {
                'title': 'test title',
                # 'teaser': 'test teaser',
                'subsections': [
                    mock.Mock(),
                    mock.Mock(),
                    mock.Mock(),
                ],
            },
            False,
        ),
        (
            {
                'title': 'test title',
                'teaser': 'test teaser',
                'subsections': [],
            },
            False,
        ),
        (
            {
                'title': 'test title',
                'teaser': 'test teaser',
                'subsections': [
                    mock.Mock(),
                ],
            },
            False,
        ),
        (
            {},
            False,
        ),
    ),
    ids=(
        'full data',
        'missing title',
        'missing teaser',
        'missing all subsections',
        'missing enough subsections',
        'no data',
    ),
)
def test_industry_accordion_is_viable(data, expected):
    assert industry_accordion_is_viable(data) == expected


@pytest.mark.parametrize(
    'data,expected',
    (
        (
            {
                'title': 'test title',
                'hero_image': mock.Mock(),
            },
            True,
        ),
        (
            {
                # 'title': 'test title',
                'hero_image': mock.Mock(),
            },
            False,
        ),
        (
            {
                'title': 'test title',
                # 'hero_image': mock.Mock(),
            },
            False,
        ),
        (
            {},
            False,
        ),
    ),
    ids=(
        'full data',
        'missing title',
        'missing hero_image',
        'no data',
    ),
)
def test_industry_accordion_case_study_is_viable(data, expected):
    assert industry_accordion_case_study_is_viable(data) == expected


@pytest.mark.parametrize(
    'attrs_to_set, expected',
    (
        (
            [
                ('article_teaser', 'article teaser text'),
                ('search_description', ''),
            ],
            'article teaser text',
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', 'article search description'),
            ],
            'article search description',
        ),
        (
            [
                ('article_teaser', 'article teaser text'),
                ('search_description', 'article search description'),
            ],
            'article teaser text',
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', ''),
                ('article_body', 'lorem ipsum dolor sit amet' * 50),
            ],
            ('lorem ipsum dolor sit amet' * 50)[:150],
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', ''),
                ('article_body', 'lorem ipsum dolor sit amet'),
            ],
            'lorem ipsum dolor sit amet',
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', ''),
                ('article_body', ''),
            ],
            '',
        ),
    ),
)
def test_get_meta_description(attrs_to_set, expected):
    page = mock.Mock()
    for attr, value in attrs_to_set:
        if attr == 'article_body':
            # special case, mocking method on article_body streamfield
            page.article_body.render_as_block.return_value = value
        else:
            setattr(page, attr, value)

    assert get_meta_description(page) == expected


def test_get_meta_description__page_none():
    assert get_meta_description(None) == ''


@pytest.mark.parametrize(
    'url,expected',
    (
        ('/foo/bar/', '/foo/bar/?'),
        ('/foo/bar/?page=2', '/foo/bar/?'),
        ('/foo/bar/?page=2&baz=3', '/foo/bar/?baz=3&'),
        ('/foo/bar/?bam=test&page=2&baz=3', '/foo/bar/?bam=test&baz=3&'),
    ),
)
def test_get_pagination_url(rf, url, expected):
    request = rf.get(url)
    assert get_pagination_url(request, 'page') == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_projected, capitalize, expected_output',
    ((True, False, 'projected'), (False, False, 'actual'), (False, True, 'Actual')),
)
def test_get_projected_or_actual(is_projected, capitalize, expected_output):
    assert get_projected_or_actual(is_projected, capitalize) == expected_output


@pytest.mark.django_db
def test_append_past_year_seperator():
    future_date = datetime.datetime.now() + datetime.timedelta(days=1)
    previous_date = datetime.datetime.now() - datetime.timedelta(days=1)
    previous_year_date = datetime.datetime.now() - datetime.timedelta(days=370)
    objects = [
        EventFactory(start_date=timezone.make_aware(future_date)),
        EventFactory(start_date=timezone.make_aware(previous_date)),
        EventFactory(start_date=timezone.make_aware(previous_date)),
        EventFactory(start_date=timezone.make_aware(previous_year_date)),
    ]
    filtered_objects = append_past_year_seperator(objects)
    assert [x.past_year_seperator for x in filtered_objects] == [
        None,
        str(future_date.year),
        None,
        str(previous_year_date.year),
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, language, expected_output',
    (
        ('http://dummy.com', QueryDict('lang=fr'), 'http://dummy.com?lang=fr'),
        ('http://dummy.com', QueryDict(''), 'http://dummy.com'),
    ),
)
def test_persist_language(url, language, expected_output):
    assert persist_language(url, language) == expected_output


def test_replace_underscores():
    assert replace_underscores('hello_world') == 'hello-world'
    assert replace_underscores('hello world') == 'hello world'


def test_replace_hyphens():
    assert replace_hyphens('hello-world') == 'hello_world'
    assert replace_hyphens('hello world') == 'hello world'


@mock.patch('domestic.helpers.get_market_widget_data_helper')
@pytest.mark.django_db
def test_get_market_widget_data(
    mock_get_market_widget_data_helper,
):
    mock_get_market_widget_data_helper.return_value = None

    result = get_market_widget_data('Chinax')

    assert result is None


def test_anchor_is_correctly_converted_to_span():
    input_html = '<p data-block-key="123"><a data-id="anchor" id="anchor" linktype="anchor-target">anchor text</a></p>'
    actual_output = convert_anchor_identifier_a_to_span(input_html)
    expected_output = '<p data-block-key="123"><span data-id="anchor" id="anchor">anchor text</span></p>'
    assert actual_output == expected_output


def test_regular_link_is_not_converted_to_span():
    input_html = '<p data-block-key="321"><a href="http://www.google.com">text for regular link</a></p>'
    actual_output = convert_anchor_identifier_a_to_span(input_html)
    expected_output = '<p data-block-key="321"><a href="http://www.google.com">text for regular link</a></p>'
    assert actual_output == expected_output


@pytest.mark.parametrize(
    'paginator,expected_outputs',
    (
        (
            Paginator([obj for obj in range(12)], 4),
            {'page_one': 1, 'page_two': 5, 'page_three': 9},
        ),
        (
            Paginator([obj for obj in range(7)], 5),
            {
                'page_one': 1,
                'page_two': 6,
            },
        ),
        (
            Paginator([obj for obj in range(27)], 10),
            {
                'page_one': 1,
                'page_two': 11,
                'page_three': 21,
            },
        ),
        (
            Paginator([obj for obj in range(123)], 10),
            {
                'page_one': 1,
                'page_two': 11,
                'page_three': 21,
                'page_fore': 31,
                'page_five': 41,
                'page_six': 51,
                'page_severn': 61,
                'page_eight': 71,
                'page_nine': 81,
                'page_ten': 91,
                'page_eleven': 101,
                'page_twelve': 111,
                'page_thirteen': 121,
            },
        ),
    ),
)
def test_pagination_obj_range_lower_limit(paginator, expected_outputs):
    count = 1
    for expected_output in expected_outputs.items():
        page_obj = paginator.page(count)
        assert pagination_obj_range_lower_limit(page_obj) == expected_output[1]
        count += 1


@pytest.mark.parametrize(
    'paginator,expected_outputs',
    (
        (
            Paginator([obj for obj in range(12)], 4),
            {'page_one': 4, 'page_two': 8, 'page_three': 12},
        ),
        (
            Paginator([obj for obj in range(7)], 5),
            {
                'page_one': 5,
                'page_two': 7,
            },
        ),
        (
            Paginator([obj for obj in range(27)], 10),
            {
                'page_one': 10,
                'page_two': 20,
                'page_three': 27,
            },
        ),
        (
            Paginator([obj for obj in range(123)], 10),
            {
                'page_one': 10,
                'page_two': 20,
                'page_three': 30,
                'page_fore': 40,
                'page_five': 50,
                'page_six': 60,
                'page_severn': 70,
                'page_eight': 80,
                'page_nine': 90,
                'page_ten': 100,
                'page_eleven': 110,
                'page_twelve': 120,
                'page_thirteen': 123,
            },
        ),
    ),
)
def test_pagination_obj_range_upper_limit(paginator, expected_outputs):
    count = 1
    for expected_output in expected_outputs.items():
        page_obj = paginator.page(count)
        assert pagination_obj_range_upper_limit(page_obj) == expected_output[1]
        count += 1
