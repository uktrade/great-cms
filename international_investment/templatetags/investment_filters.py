from django import template
from django.template.defaultfilters import urlencode

register = template.Library()


@register.filter
def get_url(value, param=None):
    if param is None:
        return value
    return f'{value}?{urlencode(param)}'


@register.simple_tag
def get_filter_accordion_items(form):
    items = []

    for field in form:
        if field.field.widget.input_type == 'checkbox':
            items.append(
                {
                    'heading': {'text': field.label},
                    'content': {'html': _create_checkbox_html(field, _get_field_values(field))},
                }
            )

    return items


def _get_field_values(field):
    if hasattr(field, 'value'):
        if callable(field.value):
            return field.value() or []
        return field.value or []
    return []


def _create_checkbox_html(field, field_values):
    checkboxes_html = (
        '<div class="govuk-checkboxes govuk-checkboxes--small fixed-height-scroll govuk-!-padding-left-2 tabindex="-1" '
        'data-module="govuk-checkboxes">'
    )

    for action in field:
        value = action.data['value'] if isinstance(action.data, dict) else action.data.value
        checked = 'checked' if value in field_values else ''
        checkboxes_html += (
            f'<div class="govuk-checkboxes__item">'
            f'<input {checked} type="checkbox" name="{field.name}" '
            f'value="{value}" class="govuk-checkboxes__input" '
            f'id="{action.id_for_label}">'
            f'<label class="govuk-label govuk-checkboxes__label" '
            f'for="{action.id_for_label}">{action.choice_label}</label>'
            f'</div>'
        )

    return checkboxes_html + '</div>'
