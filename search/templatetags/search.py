from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def map_search_result_type(content_type):
    """
    Maps the search result's (i.e. Wagtail Page object) content_type to a
    more numan readable and relevent name.
    """

    if 'Campaign' in content_type:
        return 'Campaign' 

    elif 'lesson' in content_type:
        return 'Export Academy' 
    
    elif 'Topic' or 'Task' in content_type:
       return 'Service' 
    
    else:
        return 'Article'