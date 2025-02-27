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


@register.inclusion_tag('_hero.html')
def render_ukea_homepage_hero(
    image_url,
    hero_title,
    above_cta_text,
    below_cta_text,
    action_link_label,
    action_link_internal,
    action_link_external,
):
    if not action_link_label and (action_link_internal or action_link_external):
        action_link_label = None
        action_link_url = None
    elif action_link_internal:
        action_link_url = action_link_internal
    else:
        action_link_url = action_link_external

    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'aboveCtaHtml': above_cta_text,
        'belowCtaHtml': below_cta_text,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
        'actionLinkUrl': action_link_url,
        'actionLinkText': action_link_label,
    }

    return None
