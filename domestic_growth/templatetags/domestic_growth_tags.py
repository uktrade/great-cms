from django import template
import ast

register = template.Library()

@register.filter
def dict_merge(dict1, dict2_str):
    dict2 = ast.literal_eval(dict2_str)
    if not dict1:
        dict1 = {}
    return {**dict1, **dict2}

@register.filter
def get_trade_association_tags(ta, sector):
    tags = []
    if ta.type == 'sub_sector' and sector.get('sub_sector'):
        tags.append({'text': sector['sub_sector'], 'type': 'sector'})
    elif ta.type == 'sector' and sector.get('sector'):
        tags.append({'text': sector['sector'], 'type': 'sector'})
    if ta.regions:
        tags.append({'text': ta.regions, 'type': 'location'})
    return tags
