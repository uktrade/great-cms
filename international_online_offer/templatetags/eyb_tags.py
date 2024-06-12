from django import template
from django.conf import settings

register = template.Library()


# todo: remove post election
@register.simple_tag
def feature_pre_election():
    return settings.FEATURE_PRE_ELECTION


@register.simple_tag(takes_context=True)
def get_salary_display_classes(context):
    result = {'parent_column_class': 'govuk-grid-column-full', 'salary_card_class': 'govuk-grid-column-one-third'}

    if not (context['entry_salary'] and context['mid_salary'] and context['executive_salary']):
        result['parent_column_class'] = 'govuk-grid-column-two-thirds'
        result['salary_card_class'] = 'govuk-grid-column-one-half'

    return result


@register.filter
def float_to_int(val: float) -> int:
    """
    Utility function that can be called from a django template to return the whole number
    of a decimal. Not to be confused with django's intcomma which retains the fraction part.
    """
    return int(str(val).split('.')[0])
