from django import template

register = template.Library()


@register.inclusion_tag('export_academy/includes/event_action_buttons.html', takes_context=True)
def event_list_buttons(context, event):
    view = context['view']

    context.update(
        {
            'action_buttons': view.get_buttons_for_obj(event),
        }
    )
    return context
