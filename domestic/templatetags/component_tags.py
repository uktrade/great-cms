# Refactored/amended versions of templatetags formerly in directory_componennts

from django import template

register = template.Library()


@register.inclusion_tag('core/components/directory_components/templates/directory_components/statistics_card_grid.html')
def statistics_card_grid(**kwargs):
    return kwargs
