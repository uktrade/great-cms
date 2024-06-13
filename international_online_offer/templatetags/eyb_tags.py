from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_salary_display_classes(context):
    result = {'parent_column_class': 'govuk-grid-column-full', 'salary_card_class': 'govuk-grid-column-one-third'}

    if not (context['entry_salary'] and context['mid_salary'] and context['executive_salary']):
        result['parent_column_class'] = 'govuk-grid-column-two-thirds'
        result['salary_card_class'] = 'govuk-grid-column-one-half'

    return result
