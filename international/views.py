from django.views.generic import TemplateView
from great_components.mixins import GA360Mixin


class IndexView(GA360Mixin, TemplateView):
    template_name = 'international/index.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Index',
            business_unit='International',
            site_section='index',
        )
