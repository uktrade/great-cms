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
def gt(value, arg):
    try:
        return int(value) > int(arg)
    except (ValueError, TypeError):
        return False

@register.filter
def get_trade_association_tags(ta, sector_str):
    tags = []
    try:
        sector = ast.literal_eval(str(sector_str))
        if isinstance(ta, dict):
            if ta.get('type') == 'sub_sector' and sector.get('sub_sector'):
                tags.append({'text': sector['sub_sector'], 'type': 'sector'})
            elif ta.get('type') == 'sector' and sector.get('sector'):
                tags.append({'text': sector['sector'], 'type': 'sector'})
            if ta.get('regions'):
                tags.append({'text': ta['regions'], 'type': 'location'})
    except (ValueError, SyntaxError):
        pass
    return tags

@register.filter
def create_card_attributes(value):
    if value:
        return {'data-hidden-ta': 'true'}
    return {}
