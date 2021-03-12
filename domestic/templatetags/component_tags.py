# Refactored/amended versions of templatetags formerly in directory_componennts
from bs4 import BeautifulSoup
from django import template
from django.templatetags import static

from domestic.models import ArticleListingPage, TopicLandingPage

register = template.Library()

META_DESCRIPTION_TEXT_LENGTH = 150


@register.tag
def breadcrumbs(parser, token):
    nodelist = parser.parse(('endbreadcrumbs',))
    parser.delete_first_token()
    try:
        bit = token.split_contents()[1]
    except IndexError:
        raise ValueError('Please specify the label of the current page')
    return Breadcrumbs(nodelist, bit)


class Breadcrumbs(template.Node):
    template = """
        <nav aria-label="Breadcrumb" class="breadcrumbs">
          <ol>
          </ol>
        </nav>
    """

    def __init__(self, nodelist, bit):
        self.nodelist = nodelist
        self.bit = bit

    def render(self, context):
        html = self.nodelist.render(context)
        input_soup = BeautifulSoup(html, 'html.parser')
        output_soup = BeautifulSoup(self.template, 'html.parser')
        links = input_soup.findAll('a')
        if not links:
            raise ValueError('Please specify some links')
        # adding level 1...n
        for link in links:
            if not link.get('href'):
                raise ValueError('Missing href in breadcrumb')
            element = output_soup.new_tag('li')
            element.append(link)
            output_soup.find('ol').append(element)

        # adding the current page
        current = template.Variable(self.bit).resolve(context)
        output_soup.find('ol').append(f'<li aria-current="page"><span>{current}</span></li>')
        return output_soup.decode(formatter=None)


@register.tag
def ga360_data(parser, token):
    nodelist = parser.parse(('end_ga360_data',))
    parser.delete_first_token()

    # the ga360_data tag expects arguments in the following format
    # <target> action=<action> type=<type> element=<element> value=<value>
    parameters = token.split_contents()

    target = parameters[1]
    action = None
    ga_type = None
    element = None
    value = None
    include_form_data = None

    for parameter in parameters[2:]:
        action_param_name = 'action='
        type_param_name = 'type='
        element_param_name = 'element='
        value_param_name = 'value='
        include_form_data_param_name = 'include_form_data='

        if parameter.startswith(action_param_name):
            action = parameter[len(action_param_name) :]  # noqa: E203

        elif parameter.startswith(type_param_name):
            ga_type = parameter[len(type_param_name) :]  # noqa: E203

        elif parameter.startswith(element_param_name):
            element = parameter[len(element_param_name) :]  # noqa: E203

        elif parameter.startswith(value_param_name):
            value = parameter[len(value_param_name) :]  # noqa: E203

        elif parameter.startswith(include_form_data_param_name):
            include_form_data = parameter[len(include_form_data_param_name) :]  # noqa: E203

    return GA360Data(nodelist, target, action, ga_type, element, value, include_form_data)


class GA360Data(template.Node):
    def __init__(self, nodelist, target, action=None, ga_type=None, element=None, value=None, include_form_data=None):
        self.nodelist = nodelist
        self.target = template.Variable(target)
        self.action = template.Variable(action) if action is not None else None
        self.ga_type = template.Variable(ga_type) if ga_type is not None else None
        self.element = template.Variable(element) if element is not None else None
        self.value = template.Variable(value) if value is not None else None
        self.include_form_data = template.Variable(include_form_data) if include_form_data is not None else None

    def render(self, context):
        html = self.nodelist.render(context)
        soup = BeautifulSoup(html, 'html.parser')

        selector = self.target.resolve(context)
        for element in soup.findAll(selector):
            if self.action is not None:
                element.attrs['data-ga-action'] = self.action.resolve(context)
            if self.ga_type is not None:
                element.attrs['data-ga-type'] = self.ga_type.resolve(context)
            if self.element is not None:
                element.attrs['data-ga-element'] = self.element.resolve(context)
            if self.value is not None:
                element.attrs['data-ga-value'] = self.value.resolve(context)
            if self.include_form_data is not None:
                element.attrs['data-ga-include-form-data'] = self.include_form_data.resolve(context)

        # Use formatter=None so that `&` is not converted to `&amp;`
        return soup.decode(formatter=None)


class FullStaticNode(static.StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))


@register.tag
def static_absolute(parser, token):
    return FullStaticNode.handle_token(parser, token)


@register.filter
def industry_accordion_is_viable(value):
    # Decides whether or not to show an industry accordion,
    # based on the value of a CountryGuideIndustryBlock
    if not value:
        return False

    return all([value.get('title'), value.get('teaser'), len(value.get('subsections')) > 1])


@register.filter
def industry_accordion_case_study_is_viable(value):
    # Decides whether or not to show an industry accordion,
    # based on the value of a CountryGuideCaseStudyBlock
    if not value:
        return False
    return all([value.get('title'), value.get('hero_image')])


@register.simple_tag
def get_meta_description(page):

    if not page:
        return ''

    description = page.article_teaser if page.article_teaser else page.search_description

    if not description and page.article_body:
        #  article_body is a streamfield with rich-text blocks in it

        html = BeautifulSoup(
            page.article_body.render_as_block(),
            'html.parser',
            # Note that this excludes pull quotes
        )
        body_text = html.findAll(text=True)
        description = ''.join(body_text)[:META_DESCRIPTION_TEXT_LENGTH]

    return description if description is not None else ''


# TODO? Reimplement, if we can't address this better at the Wagtail level
# @register.filter
# def add_href_target(value, request):
#     soup = BeautifulSoup(value, 'html.parser')
#     for element in soup.findAll('a', attrs={'href': re.compile('^http')}):
#         if request.META['HTTP_HOST'] not in element.attrs['href']:
#             element.attrs['target'] = '_blank'
#             element.attrs['title'] = 'Opens in a new window'
#             element.attrs['rel'] = 'noopener noreferrer'
#     return str(soup)


def get_pagination_url(request, page_param_name):
    """Remove pagination param from request url"""
    url = request.path
    params = request.GET.copy()
    params.pop(page_param_name, None)
    if params:
        return f'{url}?{params.urlencode()}&'
    return f'{url}?'


@register.inclusion_tag('components/pagination/pagination.html', takes_context=True)
def pagination(context, pagination_page, page_param_name='page'):
    paginator = pagination_page.paginator
    pagination_url = get_pagination_url(request=context['request'], page_param_name=page_param_name)
    return {
        'page_param_name': page_param_name,
        'pagination': pagination_page,
        'url': pagination_url,
        'pages_after_current': paginator.num_pages - pagination_page.number,
    }


@register.inclusion_tag('components/message_box.html')
def message_box(**kwargs):
    return kwargs


@register.inclusion_tag('components/message_box_with_icon.html')
def success_box(**kwargs):
    return {
        'icon': '✓',
        'heading_level': 'h3',
        **kwargs,
    }


@register.simple_tag
def is_descendant_of_parent_with_slug(child_page, parent_type_classname, slug_):

    parent_class = {
        'TopicLandingPage': TopicLandingPage,
        'ArticleListingPage': ArticleListingPage,
    }.get(parent_type_classname)

    if parent_class:
        for page_ in child_page.get_ancestors().specific():
            if page_.__class__ == parent_class and page_.slug == slug_:
                return True

    return False


@register.simple_tag
def is_logged_out(request):
    return not request.user.is_authenticated
