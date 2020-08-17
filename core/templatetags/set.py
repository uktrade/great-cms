from django import template
register = template.Library()

"""
Template tag to set a context variable
Usage:
    {% set 'my_field' value %}
"""


@register.simple_tag(takes_context=True)
def set(context, var_name, value):
    context[var_name] = value
    if not context.get('store'):
        context['store'] = {}
    context['store'][var_name] = value
    return ''
