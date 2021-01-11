import pytest
from bs4 import BeautifulSoup
from directory_components import forms
from directory_components.templatetags import directory_components
from directory_components.templatetags.directory_components import international_header
from django.core.paginator import Paginator
from django.template import Context, Template

REQUIRED_MESSAGE = forms.PaddedCharField.default_error_messages['required']


class PaddedTestForm(forms.Form):
    field = forms.PaddedCharField(fillchar='0', max_length=6)


def test_static_absolute(rf):
    template = Template(
        '{% load static_absolute from directory_components %}'
        '{% static_absolute "directory_components/images/favicon.ico" %}'
    )

    context = Context({'request': rf.get('/')})
    html = template.render(context)

    assert html == ('http://testserver/static/directory_components/images/favicon.ico')


def test_add_anchors():
    template = Template('{% load add_anchors from directory_components %}' '{{ html|add_anchors:"-section" }}')

    context = Context({'html': '<br/><h2>Title one</h2><h2>Title two</h2><br/>'})
    html = template.render(context)

    assert html == (
        '<br/>' '<h2 id="title-one-section">Title one</h2>' '<h2 id="title-two-section">Title two</h2>' '<br/>'
    )


def test_add_href_target(rf):
    request = rf.get('/')
    request.META['HTTP_HOST'] = 'example.com'
    template = Template(
        '{% load add_href_target from directory_components %}' '{{ html|add_href_target:request|safe }}'
    )
    context = Context(
        {
            'request': request,
            'html': (
                '<a href="http://www.google.com"></a>'
                '<a href="https://www.google.com"></a>'
                '<a href="http://www.example.com"></a>'
                '<a href="http://example.com/selling-online-overseas"></a>'
                '<a href="http://example.com/export-opportunities"></a>'
                '<a href="/selling-online-overseas"></a>'
                '<a href="/export-opportunities"></a>'
            ),
        }
    )
    html = template.render(context)

    assert html == (
        '<a href="http://www.google.com" rel="noopener noreferrer" target="_blank" title="Opens in a new window"></a>'
        '<a href="https://www.google.com" rel="noopener noreferrer" target="_blank" title="Opens in a new window"></a>'
        '<a href="http://www.example.com"></a>'
        '<a href="http://example.com/selling-online-overseas"></a>'
        '<a href="http://example.com/export-opportunities"></a>'
        '<a href="/selling-online-overseas"></a>'
        '<a href="/export-opportunities"></a>'
    )


def test_add_anchors_no_suffix():
    template = Template('{% load add_anchors from directory_components %}' '{{ html|add_anchors }}')

    context = Context({'html': '<br/><h2>Title one</h2><h2>Title two</h2><br/>'})
    html = template.render(context)

    assert html == ('<br/>' '<h2 id="title-one">Title one</h2>' '<h2 id="title-two">Title two</h2>' '<br/>')


def test_add_anchors_to_all_headings():
    template = Template(
        '{% load add_anchors_to_all_headings from directory_components %}'
        '{{ html|add_anchors_to_all_headings:"-section" }}'
    )

    context = Context(
        {'html': '<br/>' '<h1>Title one</h1>' '<h2>Title two</h2>' '<h3>Title: with punctuation!</h3>' '<br/>'}
    )
    html = template.render(context)

    assert html == (
        '<br/>'
        '<h1 id="title-one-section">Title one</h1>'
        '<h2 id="title-two-section">Title two</h2>'
        '<h3 id="title-with-punctuation-section">Title: with punctuation!</h3>'
        '<br/>'
    )


def test_add_anchors_to_all_headings_no_suffix():
    template = Template(
        '{% load add_anchors_to_all_headings from directory_components %}' '{{ html|add_anchors_to_all_headings }}'
    )

    context = Context(
        {'html': '<br/>' '<h1>Title one</h1>' '<h2>Title two</h2>' '<h3>Title: with punctuation!</h3>' '<br/>'}
    )
    html = template.render(context)

    assert html == (
        '<br/>'
        '<h1 id="title-one">Title one</h1>'
        '<h2 id="title-two">Title two</h2>'
        '<h3 id="title-with-punctuation">Title: with punctuation!</h3>'
        '<br/>'
    )


@pytest.mark.parametrize(
    'input_html,expected_html',
    (
        ('<h1>content</h1>', '<h1 class="heading-xlarge">content</h1>'),
        ('<h2>content</h2>', '<h2 class="heading-large">content</h2>'),
        ('<h3>content</h3>', '<h3 class="heading-medium">content</h3>'),
        ('<h4>content</h4>', '<h4 class="heading-small">content</h4>'),
        ('<ul>content</ul>', '<ul class="list list-bullet">content</ul>'),
        ('<ol>content</ul>', '<ol class="list list-number">content</ol>'),
        ('<p>content</p>', '<p class="body-text">content</p>'),
        ('<a>content</a>', '<a class="link">content</a>'),
        ('<blockquote>a</blockquote>', '<blockquote class="quote">a</blockquote>'),
    ),
)
def test_add_export_elements_classes(input_html, expected_html):
    template = Template(
        '{% load add_export_elements_classes from directory_components %}' '{{ html|add_export_elements_classes }}'
    )
    context = Context({'html': input_html})

    html = template.render(context)
    assert html == expected_html


def test_card():
    card_content = {
        'title': 'title',
        'url': 'url',
        'description': 'description',
        'img_src': 'img_src',
        'img_alt': 'img_alt',
    }
    string = (
        "{{% load card from directory_components %}}"
        "{{% card title='{title}' url='{url}' description='{description}' "
        "img_src='{img_src}' img_alt='{img_alt}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_link = soup.select('.card-link')[0]
    assert 'url' in card_link['href']

    card_image = soup.select('.card-image')[0]
    assert 'img_src' in card_image['src']
    assert card_image['alt'] == 'img_alt'

    card_heading = soup.select('h3.heading-large')[0]
    assert card_heading.string == 'title'

    card_description = soup.select('p.description')[0]
    assert card_description.string == 'description'


def test_card_html():
    html_content = '<p>Test</p>'
    card_content = {
        'html_content': html_content,
    }
    string = ("{{% load card from directory_components %}}" "{{% card html_content='{html_content}' %}}").format(
        **card_content
    )

    template = Template(string)
    context = Context({})

    html = template.render(context)

    assert html_content in html


def test_labelled_card_with_image():
    card_content = {
        'title': 'title',
        'url': 'url',
        'description': 'description',
        'img_src': 'img_src',
        'img_alt': 'img_alt',
    }
    string = (
        "{{% load labelled_card from directory_components %}}"
        "{{% labelled_card title='{title}' url='{url}' img_src='{img_src}' "
        "description='{description}' img_alt='{img_alt}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_link = soup.select('.labelled-card')[0]
    assert 'url' in card_link['href']

    card_inner = soup.select('div.card-inner')[0]
    assert 'with-image' in card_inner['class']

    card_image = soup.select('.card-image')[0]
    assert 'img_src' in card_image['src']
    assert card_image['alt'] == 'img_alt'

    card_heading = soup.select('h3.title')[0]
    assert card_heading.string == 'title'

    card_description = soup.select('p.description')[0]
    assert card_description.string == 'description'


def test_labelled_card_without_image():
    card_content = {
        'title': 'title',
        'url': 'url',
        'description': 'description',
    }
    string = (
        "{{% load labelled_card from directory_components %}}"
        "{{% labelled_card title='{title}' url='{url}' "
        "description='{description}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_inner = soup.select('div.card-inner')[0]
    assert 'with-image' not in card_inner['class']


def test_labelled_image_card():
    card_content = {
        'title': 'title',
        'url': 'url',
        'description': 'description',
        'img_src': 'img_src',
        'img_alt': 'img_alt',
    }
    string = (
        "{{% load labelled_image_card from directory_components %}}"
        "{{% labelled_image_card title='{title}' url='{url}' "
        "img_src='{img_src}' "
        "description='{description}' img_alt='{img_alt}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_link = soup.select('.labelled-image-card')[0]
    assert 'url' in card_link['href']

    card_image = soup.select('.card-image')[0]
    assert card_image.name == 'img'
    assert 'img_src' in card_image['src']
    assert card_image['alt'] == 'img_alt'

    card_heading = soup.select('h3.title')[0]
    assert card_heading.string == 'title'


def test_card_with_icon():
    card_content = {
        'title': 'title',
        'url': 'url',
        'description': 'description',
        'img_src': 'img_src',
        'img_alt': 'img_alt',
    }
    string = (
        "{{% load card_with_icon from directory_components %}}"
        "{{% card_with_icon title='{title}' url='{url}' "
        "description='{description}' "
        "img_src='{img_src}' img_alt='{img_alt}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_link = soup.select('.card-link')[0]
    assert 'url' in card_link['href']

    card_image = soup.find('img')
    assert card_image['src'] == 'img_src'
    assert card_image['alt'] == 'img_alt'

    card_heading = soup.select('h3.heading-large')[0]
    assert card_heading.string == 'title'

    card_description = soup.select('p.description')[0]
    assert card_description.string == 'description'


def test_card_with_external_link():
    card_content = {
        'external_link': True,
        'url': 'url',
    }
    string = (
        "{{% load card from directory_components %}}" "{{% card external_link='{external_link}' url='{url}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    card_link = soup.select('.card-link')[0]

    assert card_link['target'] == '_blank'
    assert card_link['rel'] == ['noopener', 'noreferrer']
    assert card_link['title'] == 'Opens in a new window'


def test_card_no_padding_transparent():
    card_content = {'title': 'title', 'url': 'url', 'no_padding_card': True, 'transparent_card': True}
    string = (
        "{{% load card from directory_components %}}"
        "{{% card no_padding_card='{no_padding_card}' transparent_card='{transparent_card}' %}}"
    ).format(**card_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)

    assert 'card no-padding-card transparent-card' in html


def test_message_box_default():
    box_content = {
        'heading': 'heading',
        'description': 'description',
    }
    string = (
        "{{% load message_box from directory_components %}}"
        "{{% message_box heading='{heading}' "
        "description='{description}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box_heading = soup.select('h3.heading-medium')[0]
    assert box_heading.string == 'heading'

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'


def test_message_box_custom():
    box_content = {
        'heading': 'heading',
        'heading_level': 'h4',
        'heading_class': 'great-red-text',
        'description': 'description',
        'box_class': 'border-great-red background-offwhite',
    }
    string = (
        "{{% load message_box from directory_components %}}"
        "{{% message_box heading='{heading}' heading_level='{heading_level}' "
        "heading_class='{heading_class}' description='{description}' "
        "box_class='{box_class}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box_heading = soup.select('h4.great-red-text')[0]
    assert box_heading.string == 'heading'

    box = soup.select('.message-box')[0]
    assert 'border-great-red' in box['class']
    assert 'background-offwhite' in box['class']

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'


def test_error_box():
    box_content = {
        'heading': 'heading',
        'description': 'description',
    }
    string = (
        "{{% load error_box from directory_components %}}"
        "{{% error_box heading='{heading}' "
        "description='{description}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box_heading = soup.select('h3.flag-red-text')[0]
    assert box_heading.string == 'heading'

    box = soup.select('.message-box-with-icon')[0]
    assert 'border-flag-red' in box['class']
    assert 'background-white' in box['class']

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'


def test_success_box():
    box_content = {
        'heading': 'heading',
        'description': 'description',
    }
    string = (
        "{{% load success_box from directory_components %}}"
        "{{% success_box heading='{heading}' "
        "description='{description}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box_heading = soup.select('h3.grey-text')[0]
    assert box_heading.string == 'heading'

    box = soup.select('.message-box-with-icon')[0]
    assert 'border-teal' in box['class']
    assert 'background-white' in box['class']

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'


def test_cta_box_default():
    box_content = {
        'box_id': 'box_id',
        'heading': 'heading',
        'description': 'description',
        'button_text': 'button_text',
        'button_url': 'button_url',
    }
    string = (
        "{{% load cta_box from directory_components %}}"
        "{{% cta_box box_id='{box_id}' heading='{heading}' "
        "description='{description}' "
        "button_text='{button_text}' button_url='{button_url}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box_id = soup.find(id='box_id')
    assert box_id['id'] == 'box_id'

    box_heading = soup.select('h3.heading-medium')[0]
    assert box_heading.string == 'heading'

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'

    box_button = soup.select('a.button')[0]
    assert box_button.string == 'button_text'
    assert box_button['href'] == 'button_url'


def test_cta_box_custom():
    box_content = {
        'box_id': 'box_id',
        'box_class': 'background-great-blue white-text',
        'heading': 'heading',
        'heading_level': 'h4',
        'heading_class': 'heading-small',
        'description': 'description',
        'button_text': 'button_text',
        'button_url': 'button_url',
    }
    string = (
        "{{% load cta_box from directory_components %}}"
        "{{% cta_box box_id='{box_id}' heading='{heading}' "
        "box_class='{box_class}' heading_level='{heading_level}' "
        "heading_class='{heading_class}' description='{description}' "
        "button_text='{button_text}' button_url='{button_url}' %}}"
    ).format(**box_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    box = soup.select('.cta-box')[0]
    assert box['id'] == 'box_id'

    assert 'background-great-blue' in box['class']
    assert 'white-text' in box['class']

    box_heading = soup.select('h4.heading-small')[0]
    assert box_heading.string == 'heading'

    box_description = soup.select('p.box-description')[0]
    assert box_description.string == 'description'

    box_button = soup.select('a.button')[0]
    assert box_button.string == 'button_text'
    assert box_button['href'] == 'button_url'
    assert box_button['id'] == 'box_id-button'


def test_banner():
    banner_content = {
        'badge_content': 'Badge content',
        'banner_content': '<p>Banner content with a <a href="#">link</a></p>',
    }
    string = (
        "{{% load banner from directory_components %}}"
        "{{% banner badge_content='{badge_content}' "
        "banner_content='{banner_content}' %}}"
    ).format(**banner_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    banner = soup.select('.information-banner')[0]
    assert banner['id'] == 'information-banner'

    badge = soup.select('.banner-badge span')[0]
    assert badge.string == 'Badge content'

    exp_banner_content = (
        '<div><p class="body-text">Banner content with a ' '<a class="link" href="#">link</a></p></div>'
    )

    banner_content = soup.select('.banner-content div:nth-of-type(2)')[0]
    assert str(banner_content) == exp_banner_content


def test_hero():
    hero_content = {
        'background_image_url': 'image.png',
        'hero_text': 'hero_text',
        'description': 'description',
    }
    string = (
        "{{% load hero from directory_components %}}"
        "{{% hero background_image_url='{background_image_url}' "
        "hero_text='{hero_text}' description='{description}' %}}"
    ).format(**hero_content)

    template = Template(string)
    context = Context({})

    html = template.render(context)
    soup = BeautifulSoup(html, 'html.parser')

    banner = soup.find(id='hero-heading')
    assert 'hero_text' in banner.string
    assert 'great-hero-heading' in banner['class']

    assert 'great-hero-title' in html

    banner = soup.find(id='hero-description')
    assert banner.string == 'description'


@pytest.mark.parametrize(
    'template_tag',
    (
        directory_components.cta_box,
        directory_components.message_box,
        directory_components.message_box_with_icon,
        directory_components.banner,
        directory_components.hero,
        directory_components.card,
        directory_components.card_with_icon,
        directory_components.labelled_card,
        directory_components.labelled_image_card,
        directory_components.image_with_caption,
        directory_components.cta_card,
        directory_components.cta_link,
        directory_components.statistics_card_grid,
        directory_components.hero_with_cta,
        directory_components.case_study,
        directory_components.informative_banner,
        directory_components.search_page_selected_filters,
        directory_components.search_page_expandable_options,
        directory_components.full_width_image_with_list_and_media,
        directory_components.key_facts,
        directory_components.accordion_list,
        directory_components.featured_articles,
    ),
)
def test_template_tag_kwargs(template_tag):
    test_kwargs = {
        'foo': 'foo',
        'bar': 'bar',
    }
    actual = template_tag(**test_kwargs)
    assert actual == test_kwargs


@pytest.mark.parametrize('heading', ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
def test_convert_headings_to(heading):
    actual = directory_components.convert_headings_to('<' + heading + '></' + heading + '>', 'figure')
    expected = '<figure></figure>'
    assert actual == expected


def test_convert_headings_to_does_not_convert_non_headings():
    actual = directory_components.convert_headings_to('<span></span>', 'figure')
    expected = '<span></span>'
    assert actual == expected


def test_override_elements_css_class():
    actual = directory_components.override_elements_css_class('<h2 class="existing-class"></h2>', 'h2,test-class')
    expected = '<h2 class="test-class"></h2>'
    assert actual == expected


def test_override_elements_css_class_does_not_override_non_targets():
    actual = directory_components.override_elements_css_class('<h4 class="existing-class"></h4>', 'h2,test-class')
    expected = '<h4 class="existing-class"></h4>'
    assert actual == expected


def test_lazyload():
    template = Template(
        '{% load lazyload from directory_components %}'
        '{% lazyload %}'
        '<img class="foo" src="/bar"/>'
        '{% endlazyload %}'
    )

    rendered_html = template.render(Context())

    expected_html = '<img class="foo" src="/bar"/>'
    assert rendered_html.replace('\n', '') == expected_html


def test_lazyload_no_img_class():
    template = Template(
        '{% load lazyload from directory_components %}' '{% lazyload %}' '<img src="/bar"/>' '{% endlazyload %}'
    )

    rendered_html = template.render(Context())

    expected_html = '<img src="/bar"/>'
    assert rendered_html.replace('\n', '') == expected_html


def test_lazyload_no_img_src():
    template = Template(
        '{% load lazyload from directory_components %}' '{% lazyload %}' '<img class="foo"/>' '{% endlazyload %}'
    )

    rendered_html = template.render(Context())

    expected_html = '<img class="foo"/>'
    assert rendered_html.replace('\n', '') == expected_html


def test_lazyload_context_variables():
    template = Template(
        '{% load lazyload from directory_components %}'
        '{% lazyload %}'
        '<img class="{{ foo.class }}" src="{{ foo.src }}"/>'
        '{% endlazyload %}'
    )

    context = {'foo': {'class': 'foo-class', 'src': '/foo'}}

    rendered_html = template.render(Context(context))

    expected_html = '<img class="foo-class" src="/foo"/>'
    assert rendered_html.replace('\n', '') == expected_html


def test_breadcrumbs():
    template = Template(
        '{% load breadcrumbs from directory_components %}'
        '{% breadcrumbs "Current Page" %}'
        '<a href="/foo"></a>'
        '<a href="/bar"></a>'
        '<a href="/baz"></a>'
        '{% endbreadcrumbs %}'
    )

    rendered_html = template.render(Context())

    expected_html = (
        '<nav aria-label="Breadcrumb" class="breadcrumbs">'
        '<ol>'
        '<li><a href="/foo"></a></li>'
        '<li><a href="/bar"></a></li>'
        '<li><a href="/baz"></a></li>'
        '<li aria-current="page"><span>Current Page</span></li>'
        '</ol>'
        '</nav>'
    )
    assert rendered_html.replace('\n', '') == expected_html


def test_breadcrumbs_context_variables():
    template = Template(
        '{% load breadcrumbs from directory_components %}'
        '{% breadcrumbs "Current Page" %}'
        '<a href="{{ foo.url }}">{{ foo.title }}</a>'
        '<a href="{{ bar.url }}">{{ bar.title }}</a>'
        '<a href="{{ baz.url }}">{{ baz.title }}</a>'
        '{% endbreadcrumbs %}'
    )

    context = {
        'foo': {'title': 'Foo', 'url': '/foo'},
        'bar': {'title': 'Bar', 'url': '/bar'},
        'baz': {'title': 'Baz', 'url': '/baz'},
    }

    rendered_html = template.render(Context(context))

    expected_html = (
        '<nav aria-label="Breadcrumb" class="breadcrumbs">'
        '<ol>'
        '<li><a href="/foo">Foo</a></li>'
        '<li><a href="/bar">Bar</a></li>'
        '<li><a href="/baz">Baz</a></li>'
        '<li aria-current="page"><span>Current Page</span></li>'
        '</ol>'
        '</nav>'
    )
    assert rendered_html.replace('\n', '') == expected_html


def test_breadcrumbs_empty_href():
    template = Template(
        '{% load breadcrumbs from directory_components %}'
        '{% breadcrumbs "Current Page" %}'
        '<a href=""></a>'
        '{% endbreadcrumbs %}'
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_breadcrumbs_missing_href():
    template = Template(
        '{% load breadcrumbs from directory_components %}'
        '{% breadcrumbs "Current Page" %}'
        '<a></a>'
        '{% endbreadcrumbs %}'
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_breadcrumbs_missing_links():
    template = Template(
        '{% load breadcrumbs from directory_components %}' '{% breadcrumbs "Current Page" %}' '{% endbreadcrumbs %}'
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_breadcrumbs_missing_current_page():
    with pytest.raises(ValueError):
        Template(
            '{% load breadcrumbs from directory_components %}'
            '{% breadcrumbs %}'
            '<a href="/foo"></a>'
            '{% endbreadcrumbs %}'
        )


def test_ga360_data_with_no_optional_parameters():
    template = Template(
        '{% load ga360_data from directory_components %}'
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
        '{% load ga360_data from directory_components %}'
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
        '{% load pagination from directory_components %}' '{% pagination pagination_page=pagination_page %}'
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


class NavNode:
    def __init__(self, tier_one_item, tier_two_items):
        self.tier_one_item = tier_one_item
        self.tier_two_items = tier_two_items


class NavItem:
    def __init__(self, title, name):
        self.title = title
        self.name = name
        self.url = "/{0}/".format(name)


SAMPLE_NAVIGATION_TREE = [
    NavNode(
        tier_one_item=NavItem('Root 1', 'root-1'),
        tier_two_items=[
            NavItem('Sub Page 1', 'sub-page-1'),
        ],
    ),
    NavNode(tier_one_item=NavItem('Root 2', 'root-2'), tier_two_items=[]),
]


@pytest.mark.parametrize(
    'section,subsection',
    [
        ('', ''),
        ('incorrect-section', ''),
        ('', 'incorrect-subsection'),
        ('', 'sub-page-one'),
    ],
)
def test_international_header_no_active_sections(section, subsection):
    navigation = international_header(Context({}), SAMPLE_NAVIGATION_TREE, '', '')

    assert len(navigation['tier_one_items']) == 2
    assert navigation['tier_one_items'][0].title == 'Root 1'
    assert navigation['tier_one_items'][0].is_active is False
    assert navigation['tier_one_items'][1].title == 'Root 2'
    assert navigation['tier_one_items'][1].is_active is False

    assert len(navigation['tier_two_items']) == 0

    assert navigation['navigation_tree'] == SAMPLE_NAVIGATION_TREE


def test_international_header_active_section():
    navigation = international_header(Context({}), SAMPLE_NAVIGATION_TREE, 'root-1', '')

    assert len(navigation['tier_one_items']) == 2
    assert navigation['tier_one_items'][0].is_active is True
    assert navigation['tier_one_items'][1].is_active is False

    assert len(navigation['tier_two_items']) == 1
    assert navigation['tier_two_items'][0].title == 'Sub Page 1'
    assert not navigation['tier_two_items'][0].is_active


def test_international_header_active_section_and_subsection():
    navigation = international_header(Context({}), SAMPLE_NAVIGATION_TREE, 'root-1', 'sub-page-1')

    assert len(navigation['tier_one_items']) == 2
    assert navigation['tier_one_items'][0].is_active is True
    assert navigation['tier_one_items'][1].is_active is False

    assert len(navigation['tier_two_items']) == 1
    assert navigation['tier_two_items'][0].title == 'Sub Page 1'
    assert navigation['tier_two_items'][0].is_active


def test_international_header_tag():
    template = Template(
        '{% load international_header from directory_components %}'
        '{% international_header navigation_tree=tree site_section=section site_sub_section=sub_section %}'
    )
    context = {
        'tree': SAMPLE_NAVIGATION_TREE,
        'section': '',
        'sub_section': '',
    }

    html = template.render(Context(context))

    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find('a', {'href': '/root-1/'}) is not None


def test_invest_header_tag():
    template = Template(
        '{% load invest_header from directory_components %}'
        '{% invest_header navigation_tree=tree site_section=section site_sub_section=sub_section %}'
    )
    context = {
        'tree': SAMPLE_NAVIGATION_TREE,
        'section': '',
        'sub_section': '',
    }

    html = template.render(Context(context))

    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find('a', {'href': '/root-1/'}) is not None


def test_content_404_tag():
    template = Template(
        '{% load content_404 from directory_components %}'
        '{% content_404 feedback_url="/feedback/" home_page_url="/" %}'
    )

    html = template.render(Context({}))

    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find('a', {'href': '/feedback/'}) is not None
    assert soup.find('a', {'href': '/'}) is not None


def test_content_500_tag():
    template = Template(
        '{% load content_500 from directory_components %}'
        '{% content_500 feedback_url="/feedback/" home_page_url="/" %}'
    )

    html = template.render(Context({}))

    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find('a', {'href': '/feedback/'}) is not None
    assert soup.find('a', {'href': '/'}) is not None
