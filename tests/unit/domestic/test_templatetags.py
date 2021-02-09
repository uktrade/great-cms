from unittest import mock

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import override_settings

from domestic.templatetags.component_tags import (
    get_meta_description,
    get_pagination_url,
    industry_accordion_case_study_is_viable,
    industry_accordion_is_viable,
)


def test_static_absolute(rf):
    template = Template(
        '{% load static_absolute from component_tags %}'
        '{% static_absolute "images/favicon.ico" %}'
    )

    context = Context({'request': rf.get('/')})
    html = template.render(context)

    assert html == ('http://testserver/static/images/favicon.ico')


def test_breadcrumbs_simple(rf):
    # TODO: add exhaustive testing of this tag

    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs "Examples" %}'
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
        '<li><a href="/path/to/">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something">EXAMPLE LINK TWO</a></li>'
        '<li aria-current="page"><span>Examples</span></li>'
        '</ol>\n'
        '</nav>\n</div>'
    )


def test_breadcrumbs_simple__root_url_override(rf):
    #  Tests our ability to override the URL for the hard-coded root breadcrumb
    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs "Examples" %}'
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
        '<li><a href="https://great.gov.uk/">great.gov.uk</a></li>'
        '<li><a href="/path/to/">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something">EXAMPLE LINK TWO</a></li>'
        '<li aria-current="page"><span>Examples</span></li>'
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
        '<li><a href="http://test.example.com/">great.gov.uk</a></li>'
        '<li><a href="/path/to/">EXAMPLE LINK ONE</a></li>'
        '<li><a href="/path/to/something">EXAMPLE LINK TWO</a></li>'
        '<li aria-current="page"><span>Examples</span></li>'
        '</ol>\n'
        '</nav>\n</div>'
    )


def test_breadcrumb_missing_label():
    with pytest.raises(ValueError) as ctx:
        Template(
            '{% load breadcrumbs from component_tags %}'
            '{% breadcrumbs %}'
            '<a href="/foo"></a>'
            '{% endbreadcrumbs %}'
        )
        assert ctx.message == 'Please specify the label of the current page'


def test_breadcrumb_missing_href(rf):
    template = Template(
        '{% load breadcrumbs from component_tags %}'
        '{% block breadcrumbs %}'
        '<div class="container">'
        '{% breadcrumbs "EXAMPLE" %}'
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
        '{% breadcrumbs "EXAMPLE" %}'
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


@pytest.mark.parametrize(
    'count,current,expected',
    (
        (21, 1, '[1] 2 3 4 5 N'),
        (21, 2, 'P 1 [2] 3 4 5 N'),
        (21, 3, 'P 1 2 [3] 4 5 N'),
        (21, 4, 'P 1 2 3 [4] 5 N'),
        (21, 5, 'P 1 2 3 4 [5]'),
        (30, 1, '[1] 2 3 4 5 6 N'),
        (40, 1, '[1] 2 3 4 ... 8 N'),
        (40, 2, 'P 1 [2] 3 4 ... 8 N'),
        (40, 3, 'P 1 2 [3] 4 ... 8 N'),
        (40, 4, 'P 1 2 3 [4] ... 8 N'),
        (40, 5, 'P 1 ... [5] 6 7 8 N'),
        (40, 6, 'P 1 ... 5 [6] 7 8 N'),
        (40, 7, 'P 1 ... 5 6 [7] 8 N'),
        (40, 8, 'P 1 ... 5 6 7 [8]'),
        (60, 1, '[1] 2 3 4 ... 12 N'),
        (60, 2, 'P 1 [2] 3 4 ... 12 N'),
        (60, 3, 'P 1 2 [3] 4 ... 12 N'),
        (60, 4, 'P 1 2 3 [4] ... 12 N'),
        (60, 5, 'P 1 ... 4 [5] 6 ... 12 N'),
        (60, 6, 'P 1 ... 5 [6] 7 ... 12 N'),
        (60, 7, 'P 1 ... 6 [7] 8 ... 12 N'),
        (60, 8, 'P 1 ... 7 [8] 9 ... 12 N'),
        (60, 9, 'P 1 ... [9] 10 11 12 N'),
        (60, 10, 'P 1 ... 9 [10] 11 12 N'),
        (60, 11, 'P 1 ... 9 10 [11] 12 N'),
        (60, 12, 'P 1 ... 9 10 11 [12]'),
    ),
)
def test_pagination(count, current, expected, rf):
    template = Template(
        """
            {% load pagination from component_tags %}
            {% pagination pagination_page=pagination_page %}
        """
    )

    page_size = 5
    objects = [item for item in range(count)]

    paginator = Paginator(objects, page_size)
    pagination_page = paginator.page(current)
    context = {'request': rf.get('/'), 'pagination_page': pagination_page}

    html = template.render(Context(context))

    soup = BeautifulSoup(html, 'html.parser')

    items = []
    if soup.findAll('a', {'class': 'pagination-previous'}):
        items.append('P')
    for element in soup.find_all('li'):
        if element.find('span'):
            items.append('...')
        else:
            button = element.find('a')
            if 'button' in button['class']:
                items.append(f'[{button.string}]')
            else:
                items.append(button.string)
    if soup.findAll('a', {'class': 'pagination-next'}):
        items.append('N')
    assert ' '.join(items) == expected
