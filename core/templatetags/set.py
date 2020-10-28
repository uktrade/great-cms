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


@register.simple_tag(takes_context=True)
def push(context, var_name, value):
    if not context.get('store'):
        context['store'] = {}
    context['store'][var_name] = (context['store'].get(var_name) or [])
    context['store'][var_name].append(value)
    context[var_name] = context['store'][var_name]
    return ''
