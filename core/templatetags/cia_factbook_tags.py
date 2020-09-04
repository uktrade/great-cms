from django import template

register = template.Library()


@register.filter
def get_language_note(factbook_data):
    if hasattr(factbook_data, 'get') and factbook_data.get('cia_factbook_data'):
        if factbook_data.get('cia_factbook_data').get('languages'):
            return factbook_data.get('cia_factbook_data').get('languages').get('note', '')
    return ''


@register.filter
def get_language_list(factbook_data):
    if hasattr(factbook_data, 'get') and factbook_data.get('cia_factbook_data'):
        if factbook_data.get('cia_factbook_data').get('languages'):
            return factbook_data.get('cia_factbook_data').get('languages').get('note', '')
    return ''