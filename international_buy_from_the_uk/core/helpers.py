def get_url(form):
    url = '?q=' + form.cleaned_data['q']

    if form.cleaned_data['industries']:
        industries = form.cleaned_data['industries']
        for industry in industries:
            url += '&industries=' + industry

    return url
