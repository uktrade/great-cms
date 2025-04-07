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


@register.filter
def format_for_results_list(search_results):
    """
    Transforms search results into the format expected by the _results-list.html component
    """
    formatted_results = []

    for result in search_results:
        formatted_result = {
            'title': result.seo_title or result.title,
            'href': result.url,
            'type': map_search_result_type(result.content_type),
            'description': (
                result.search_description
                or getattr(result.specific, 'seo_description', '')
                or getattr(result.specific, 'search_description', '')
                or getattr(result.specific, 'featured_description', '')
                or getattr(result.specific, 'heading_teaser', '')
                or getattr(result.specific, 'teaser', '')
                or getattr(result.specific, 'page_teaser', '')
                or getattr(result.specific, 'page_subheading', '')
                or 'No description available'
            ),
        }

        # Add metadata if available
        if hasattr(result, 'first_published_at') or hasattr(result, 'last_published_at'):
            formatted_result['metadata'] = []

            if hasattr(result, 'first_published_at') and result.first_published_at:
                formatted_result['metadata'].append(
                    {
                        'datePrefix': 'Published',
                        'dateString': result.first_published_at.strftime('%d %B %Y'),
                        'datetime': result.first_published_at.strftime('%Y-%m-%d'),
                    }
                )

            if hasattr(result, 'last_published_at') and result.last_published_at:
                formatted_result['metadata'].append(
                    {
                        'datePrefix': 'Updated',
                        'dateString': result.last_published_at.strftime('%d %B %Y'),
                        'datetime': result.last_published_at.strftime('%Y-%m-%d'),
                    }
                )

        formatted_results.append(formatted_result)

    return formatted_results


@register.inclusion_tag('search/templates/search_icon.html')
def search_icon():
    return {}
