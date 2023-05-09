from django import template

from export_academy.helpers import is_export_academy_registered

register = template.Library()


@register.inclusion_tag('export_academy/includes/event_action_buttons.html', takes_context=True)
def event_list_buttons(context, event):
    view = context['view']

    context.update({'action_buttons': view.get_buttons_for_event(event), 'is_completed': event.completed})
    return context


@register.inclusion_tag('export_academy/includes/event_badges.html', takes_context=True)
def event_list_badges(context, event):
    view = context['view']

    context.update({'badges': view.get_badges_for_event(event)})
    return context


@register.simple_tag(takes_context=True)
def is_logged_in(context):
    request = context['request']
    if is_export_academy_registered(request.user):
        return True

    return False


@register.filter
def disable_period_radios(value):
    return value.replace('name="period"', 'name="period" disabled')


@register.filter
def set_all_events(value):
    return value.replace('name="booking_period" value="all"', 'name="booking_period" value="all" checked')


@register.filter
def get_filters(list_of_filters, user):
    if is_export_academy_registered(user):
        return list_of_filters
    else:
        return [field for field in list_of_filters if field.name != 'booking_period']
