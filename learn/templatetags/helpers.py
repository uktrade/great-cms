from django import template
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page

from core.models import UKEACTA, RelatedContentCTA
from export_academy.models import Event

register = template.Library()


@register.simple_tag
def get_cta_attributes(cta: RelatedContentCTA):
    result = {}
    if isinstance(cta.link[0].value, Page):
        result['link'] = cta.link[0].value.relative_url(cta.link[0].value.get_site())
    else:
        result['link'] = cta.link[0].value

    if result['link'] is None:
        result['link'] = ''

    result['heading_class'] = f"govuk-body-s {'great-card__link--external' if 'http' in result['link'] else ''}"
    result['is_external_link'] = True if 'http' in result['link'] else False
    result['tag_description'] = dict(RelatedContentCTA.type_choices)[cta.type]
    result['tag_icon'] = '/static/icons/hand.svg' if 'service' in cta.type.lower() else '/static/icons/guidance.svg'
    return result


def get_first_available_event(event_ids: list):
    first_available_event = None
    for event in Event.objects.filter(id__in=event_ids).order_by('start_date'):
        if event.start_date > timezone.now() and event.live and not event.completed:
            return event
    return first_available_event


@register.simple_tag
def get_article_cta_attributes(cta: UKEACTA) -> dict:
    default_data = {
        'link': '/export-academy',
        'image': '/static/images/ukea-landing.png',
        'icon': '/static/icons/hand.svg',
        'title': 'Join the UK Export Academy',
        'description': 'Free training with Q&A, helping you learn to sell confidently to overseas customers',
        'type': 'Service',
    }
    if not cta:
        return default_data

    links = cta.ukea_cta_links.all()
    series = [
        {
            'title': link.series.title,
            'description': link.series.summary,
            'icon': '/static/icons/series-icon.jpeg',
            'type': 'Series',
            'image': cta.image[0].value[0].value.file.url if cta.image else default_data['image'],
            'link': reverse('export_academy:course', kwargs={'slug': link.series.slug}),
        }
        for link in links
        if link.series
    ]
    # We want pass through the first available event to the CTA
    # The default result will be used if first_available_event is None
    first_available_event = get_first_available_event([link.event.id for link in links if link.event])

    if first_available_event:
        return {
            'title': first_available_event.name,
            'description': first_available_event.description,
            'icon': '/static/icons/event-icon.jpeg',
            'type': 'Event',
            'image': cta.image[0].value[0].value.file.url if cta.image else default_data['image'],
            'link': first_available_event.get_absolute_url(),
        }
    elif series:
        return series[0]
    else:
        # the default CTA will be displayed if series and first available_event are None
        return default_data
