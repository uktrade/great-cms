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
    hero_description_part_1,
    hero_description_part_2,
    action_link_label,
    action_link_internal,
    action_link_external,
):
    if not (action_link_internal or action_link_external):
        action_link_label = None
        action_link_url = None
    elif action_link_internal:
        action_link_url = action_link_internal.url
    else:
        action_link_url = action_link_external

    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'descriptionHtml': hero_description_part_1,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
        'actionLinkUrl': action_link_url,
        'actionLinkText': action_link_label,
    }

    return None
