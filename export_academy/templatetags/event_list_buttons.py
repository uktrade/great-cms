from django import template
from django.contrib.auth.models import AnonymousUser

from export_academy import helpers
from export_academy.filters import EventFilter

register = template.Library()


@register.inclusion_tag('export_academy/includes/event_action_buttons.html', takes_context=True)
def event_list_buttons(context, event):
    view = context['view']
    request = context['request']
    context.update(
        {
            'action_buttons': view.get_buttons_for_event(event),
            'is_completed': event.completed,
            'signed_in': True if request.user != AnonymousUser() else False,
        }
    )
    return context


@register.inclusion_tag('export_academy/includes/event_badges.html', takes_context=True)
def event_list_badges(context, event):
    view = context['view']

    context.update({'badges': view.get_badges_for_event(event)})
    return context


@register.simple_tag(takes_context=True)
def is_logged_in(context):
    request = context['request']
    if helpers.is_export_academy_registered(request.user):
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
    if user.is_authenticated:
        return list_of_filters
    return [field for field in list_of_filters if field.name != 'booking_period']


@register.simple_tag
def user_is_booked_on_event(user, event):
    return helpers.user_booked_on_event(user, event)


def _get_display_text_for_filter_choices(filter_choices, filter_form, filter_type):
    filters = []
    for filter_choice in filter_choices:
        for value, text in filter_form.fields[filter_type].choices:
            if str(value) == filter_choice and value != EventFilter.ALL:
                filters.append(text)
    return filters


@register.simple_tag
def get_applied_filters(filter_form):
    """Get selected filters from form data, get their display text
    from the field choices and add them to applied_filters.
    """
    filters_to_display = [filter for filter in filter_form.fields.keys() if filter != 'booking_period']
    applied_filters = []
    for filter_type, filter_choices in filter_form.data.lists():
        if filter_type in filters_to_display:
            applied_filters += _get_display_text_for_filter_choices(filter_choices, filter_form, filter_type)
    return applied_filters


@register.simple_tag
def all_booking_periods_showing(query_params):
    booking_period = query_params.get('booking_period')
    return booking_period == 'all' or not booking_period
