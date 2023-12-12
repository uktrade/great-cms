from django import template
from wagtail.models import Page

from config.settings import BASE_URL
from core.models import RelatedContentCTA

register = template.Library()


@register.simple_tag
def get_cta_attributes(cta: RelatedContentCTA):
    result = {}
    result['link'] = cta.link[0].value.full_url if isinstance(cta.link[0].value, Page) else cta.link[0].value
    result['heading_class'] = f"govuk-body-s {'' if BASE_URL in result['link'] else 'great-card__link--external'}"
    result['tag_description'] = dict(RelatedContentCTA.type_choices)[cta.type]
    result['tag_icon'] = "/static/icons/hand.svg" if 'service' in cta.type.lower() else "/static/icons/guidance.svg"
    return result
