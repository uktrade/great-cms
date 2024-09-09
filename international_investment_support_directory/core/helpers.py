def get_url(form):
    base_url = '?q=' + form.cleaned_data.get('q', '')
    params = [
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
        values = form.cleaned_data.get(param)
        if values:
            base_url += ''.join(f'&{param}={value}' for value in values)

    return base_url
