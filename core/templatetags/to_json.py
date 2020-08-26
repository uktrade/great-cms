import json
from django.utils.safestring import mark_safe
from django import template

register = template.Library()

"""
A template filter to display data in JSON format - useful when debugging the UI.

Usage:
    {% data|to_json %}
"""


@register.filter
def to_json(data, indent=None):
    return mark_safe(json.dumps(data, sort_keys=True, indent=indent).replace("'", '&#39;'))
