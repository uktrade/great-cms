from django import template

register = template.Library()


@register.inclusion_tag("export_academy/includes/event_action_buttons.html", takes_context=True)
def event_list_buttons(context, index):
    obj = context['object_list'][index]
    view = context['view']
    # row_attrs_dict = view.model_admin.get_extra_attrs_for_row(obj, context)
    # row_attrs_dict['data-object-pk'] = obj.pk

    # get action buttons here -

    context.update(
        {
            'obj': obj,
            # 'row_attrs': mark_safe(flatatt(row_attrs_dict)),
            'action_buttons': view.get_buttons_for_obj(obj),
        }
    )
    return context
