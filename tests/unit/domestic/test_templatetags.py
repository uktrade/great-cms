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


# # TODO: make this work to complete coverage of the module
# def test_breadcrumb_missing_label(rf):
#     template = Template(
#         '{% load breadcrumbs from component_tags %}'
#         '{% block breadcrumbs %}'
#         '<div class="container">'
#         '{% breadcrumbs %}'  # MISSING THE LABEL
#         '<a href="/path/to/">EXAMPLE LINK ONE</a>'
#         '<a href="/path/to/something">EXAMPLE LINK TWO</a>'
#         '{% endbreadcrumbs %}'
#         '</div>'
#         '{% endblock %}'
#     )

#     context = Context({'request': rf.get('/')})
#     # For some reason pytest.raises won't catch the ValueError here
#     #  and neither does a try/except!
#     try:
#         template.render(context)
#         assert False, 'Expected a failure'
#     except ValueError as e:
#         assert e.message == 'Please specify the label of the current page'


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
