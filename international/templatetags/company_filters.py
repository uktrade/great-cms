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


@register.filter
def get_case_study_url(case_study_pk):
    url = reverse_lazy(
        'international_buy_from_the_uk:find-a-supplier-case-study', kwargs={'case_study_id': case_study_pk}
    )
    return url


@register.filter
def get_isd_case_study_url(case_study_pk):
    url = reverse_lazy(
        'international_investment_support_directory:specialist-case-study', kwargs={'case_study_id': case_study_pk}
    )
    return url
