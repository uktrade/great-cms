from django import template
from wagtail.models import Page

from core.models import RelatedContentCTA

register = template.Library()


@register.simple_tag
def get_cta_attributes(cta: RelatedContentCTA):
    result = {}
    if isinstance(cta.link[0].value, Page):
        result['link'] = cta.link[0].value.relative_url(cta.link[0].value.get_site())
    else:
        result['link'] = cta.link[0].value

    result['heading_class'] = f"govuk-body-s {'great-card__link--external' if 'http' in result['link'] else ''}"
    result['tag_description'] = dict(RelatedContentCTA.type_choices)[cta.type]
    result['tag_icon'] = '/static/icons/hand.svg' if 'service' in cta.type.lower() else '/static/icons/guidance.svg'
    return result
