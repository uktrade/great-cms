from django import template

register = template.Library()


@register.filter
def get_url(request):
    url = '?q=' + request.GET.get('q')
    if request.GET.getlist('industries'):
        industries = request.GET.getlist('industries')
        for industry in industries:
            url += '&industries=' + industry
    return url
