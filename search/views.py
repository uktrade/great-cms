from django.conf import settings
from django.shortcuts import render


def key_pages_for_indexing(request):
    """Returns data on key pages (such as the Get Finance homepage) to
    include in search that are otherwise not provided via other APIs.

    Note that while the document structure is JSON, it's returned
    as text/html.

    This was called SearchKeyPagesView in Great V1, where it was not
    configurable with settings.BASE_URL
    """

    base_url = settings.BASE_URL
    if base_url[-1] == '/':
        base_url = base_url[:-1]

    return render(
        request=request,
        context={
            'base_url': base_url,
        },
        template_name='search-key-pages.json',
    )
