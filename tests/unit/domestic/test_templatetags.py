from unittest import mock

import pytest
from django.template import Context, Template

from domestic.templatetags.component_tags import (
    get_meta_description,
    industry_accordion_case_study_is_viable,
    industry_accordion_is_viable,
    parse_date,
)


def test_static_absolute(rf):
    template = Template(
        '{% load static_absolute from component_tags %}'
        '{% static_absolute "directory_components/images/favicon.ico" %}'
    )

    context = Context({'request': rf.get('/')})
    html = template.render(context)

    assert html == ('http://testserver/static/directory_components/images/favicon.ico')


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
    'input_val, expected',
    (
        ('2021-03-05', '05 March 2021'),
        ('03-05-2021', '05 March 2021'),  # NB: North American parsing
        ('2021-03-05', '05 March 2021'),
        ('March 5th 2021', '05 March 2021'),
        (None, None),
    ),
)
def test_parse_date(input_val, expected):
    assert parse_date(input_val) == expected


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
                ('article_body_text', 'lorem ipsum dolor sit amet' * 50),
            ],
            ('lorem ipsum dolor sit amet' * 50)[:150],
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', ''),
                ('article_body_text', 'lorem ipsum dolor sit amet'),
            ],
            'lorem ipsum dolor sit amet',
        ),
        (
            [
                ('article_teaser', ''),
                ('search_description', ''),
                ('article_body_text', ''),
            ],
            '',
        ),
    ),
)
def test_get_meta_description(attrs_to_set, expected):

    page = mock.Mock()
    for attr, value in attrs_to_set:
        setattr(page, attr, value)

    assert get_meta_description(page) == expected
