from wagtail.core.models import Page

from core import mixins


class DomesticHomePage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AnonymousUserRequired,
    Page,
):
    parent_page_types = ['wagtailcore.Page']

    def get_template(self, request, *args, **kwargs):
        return ['learn/learn_page.html']
