from django import template
import ast
import logging

register = template.Library()
logger = logging.getLogger(__name__)


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
def get_trade_association_tags(ta, sector):
    tags = []
    try:
        if isinstance(ta, dict):
            if ta.get('type') == 'sub_sector':
                tags.append({'text': sector, 'type': 'sector'})
            elif ta.get('type') == 'sector':
                tags.append({'text': sector, 'type': 'sector'})
            if ta.get('regions'):
                tags.append({'text': ta['regions'], 'type': 'location'})
    except Exception as e:
        logger.error('Error in get_trade_association_tags: %s, ta: %s, sector: %s', e, ta, sector)
    return tags


@register.filter
def create_card_attributes(value):
    if value:
        return {'data-hidden-ta': 'true'}
    return {}
