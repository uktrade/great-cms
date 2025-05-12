from django import template
from django.conf import settings

from core.helpers import is_bgs_site_from_request

register = template.Library()


@register.simple_tag(takes_context=True)
def google_tag_manager_id_tag(context):
    request = context['request']
    if not settings.BGS_GOOGLE_TAG_MANAGER_ID:
        return settings.GOOGLE_TAG_MANAGER_ID
    elif not is_bgs_site_from_request(request):
        return settings.GOOGLE_TAG_MANAGER_ID
    else:
        return settings.BGS_GOOGLE_TAG_MANAGER_ID
