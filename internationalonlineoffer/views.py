from django.views.generic import TemplateView
from great_components.mixins import GA360Mixin


class IOOMixin:
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class IOOIndex(GA360Mixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='IOOIndex',
            business_unit='IOO',
            site_section='ioo',
        )

    template_name = 'ioo/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
