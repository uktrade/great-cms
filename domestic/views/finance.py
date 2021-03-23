from django.views.generic import TemplateView

from core.mixins import GetSnippetContentMixin


class TradeFinanceView(GetSnippetContentMixin, TemplateView):
    template_name = 'domestic/finance/trade_finance.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            # note that this content_snippet is also used for SEO descripton in base.html
            content_snippet=self.get_snippet_instance(),
        )
