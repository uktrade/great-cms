from django import template

register = template.Library()


@register.filter
def get_url(request):
    base_url = '?'
    params = [
        'sector',
        'region',
        'investment_type',
    ]

    for param in params:
        values = request.GET.getlist(param)
        if values:
            base_url += ''.join(f'&{param}={value}' for value in values)

    return base_url
