import pytest
from django.template import Context, Template


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
