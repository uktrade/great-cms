from django import template
from django.urls import reverse_lazy

register = template.Library()


@register.filter
def get_url(request):
    base_url = '?q=' + request.GET.get('q', '')
    params = [
        'industries',
        'expertise_industries',
        'expertise_regions',
        'expertise_countries',
        'expertise_languages',
        'expertise_products_services_financial',
        'expertise_products_services_management',
        'expertise_products_services_human_resources',
        'expertise_products_services_legal',
        'expertise_products_services_publicity',
        'expertise_products_services_business_support',
    ]

    for param in params:
        values = request.GET.getlist(param)
        if values:
            base_url += ''.join(f'&{param}={value}' for value in values)

    return base_url


@register.simple_tag()
def get_case_study_url(case_study_pk):
    url = reverse_lazy(
        'international_buy_from_the_uk:find-a-supplier-case-study', kwargs={'case_study_id': case_study_pk}
    )
    return url


@register.simple_tag()
def get_isd_case_study_url(case_study_pk):
    url = reverse_lazy(
        'international_investment_support_directory:specialist-case-study', kwargs={'case_study_id': case_study_pk}
    )
    return url


@register.simple_tag()
def append_search_back_url(url, search_url):
    if '?back=' in search_url:
        search_url = search_url.split('back=', 1)[1]
    url += '?back=' + search_url
    return url


@register.simple_tag
def get_filter_accordion_items(form):
    items = []

    for index, field in enumerate(form, 1):
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
        '<div class="govuk-checkboxes govuk-checkboxes--small fixed-height-scroll govuk-!-padding-left-2" '
        'data-module="govuk-checkboxes" '
        'tabindex="-1"> '
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
