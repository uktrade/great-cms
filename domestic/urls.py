from django.urls import path
from great_components.decorators import skip_ga360

from core import snippet_slugs
from domestic.views.finance import TradeFinanceView

app_name = 'domestic'

urlpatterns = [
    path(
        'trade-finance/',
        skip_ga360(TradeFinanceView.as_view()),
        {
            'slug': snippet_slugs.GREAT_TRADE_FINANCE,
            'snippet_import_path': 'domestic.models.TradeFinanceSnippet',
            # see core.mixins.GetSnippetContentMixin
        },
        name='trade-finance',
    ),
]
