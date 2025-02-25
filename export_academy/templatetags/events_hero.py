from django import template


register = template.Library()


@register.inclusion_tag('_hero.html')
def render_events_hero(image_url, hero_title, text, conditional_text):
    description_html = text + '<br>' + conditional_text
    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'descriptionHtml': description_html,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
    }
