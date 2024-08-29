from django import template
from django.urls import reverse_lazy

register = template.Library()


@register.filter
def get_url(request):
    url = '?q=' + request.GET.get('q')
    if request.GET.getlist('industries'):
        industries = request.GET.getlist('industries')
        for industry in industries:
            url += '&industries=' + industry
    return url


@register.filter
def get_case_study_url(case_study_pk):
    url = reverse_lazy(
        'international_buy_from_the_uk:find-a-supplier-case-study', kwargs={'case_study_id': case_study_pk}
    )
    return url
