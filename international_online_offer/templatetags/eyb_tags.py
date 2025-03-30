from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_salary_display_classes(context):
    result = {'parent_column_class': 'govuk-grid-column-full', 'salary_card_class': 'govuk-grid-column-one-third'}

    if not (context['entry_salary'] and context['mid_salary'] and context['executive_salary']):
        result['parent_column_class'] = 'govuk-grid-column-two-thirds'
        result['salary_card_class'] = 'govuk-grid-column-one-half'

    return result

@register.tag(name="capture")
def do_capture(parser, token):
    """
    Capture the content of a block into a variable.
    
    Usage:
    {% capture variable_name %}
        ... content ...
    {% endcapture %}
    """
    try:
        tag_name, variable_name = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'capture' node requires a variable name.")

    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()

    return CaptureNode(nodelist, variable_name)

class CaptureNode(template.Node):
    def __init__(self, nodelist, variable_name):
        self.nodelist = nodelist
        self.variable_name = variable_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.variable_name] = output
        return ''
