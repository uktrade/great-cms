from django.views.generic import TemplateView


class SearchKeyPagesView(TemplateView):
    """Returns data on key pages (such as the Get Finance homepage) to
    include in search that are otherwise not provided via other APIs.
    """

    template_name = 'search-key-pages.json'
