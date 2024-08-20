from django import template

register = template.Library()


@register.filter
def get_url(request):
    url = '?'
    url += 'q=' + request.GET.get('q')
    industries = request.GET.getlist('industries')
    for industry in industries:
        url += '&industries=' + industry
    return url
