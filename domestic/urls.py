from django.urls import path
from django.views.generic import TemplateView
from great_components.decorators import skip_ga360

import domestic.views.finance
import domestic.views.ukef
from core import snippet_slugs

app_name = 'domestic'

urlpatterns = [
    path(
        'get-finance/',
        skip_ga360(domestic.views.ukef.UKEFHomeView.as_view()),
        name='get-finance',
    ),
    path(
        'trade-finance/',
        skip_ga360(domestic.views.finance.TradeFinanceView.as_view()),
        {
            'slug': snippet_slugs.GREAT_TRADE_FINANCE,
            'snippet_import_path': 'domestic.models.TradeFinanceSnippet',
            # see core.mixins.GetSnippetContentMixin
        },
        name='trade-finance',
    ),
    path(
        'project-finance/',
        skip_ga360(
            domestic.views.ukef.TemplateView.as_view(
                template_name='domestic/ukef/project_finance.html',
            )
        ),
        name='project-finance',
    ),
    path(
        'how-we-assess-your-project/',
        skip_ga360(
            TemplateView.as_view(
                template_name='domestic/ukef/how_we_assess.html',
            )
        ),
        name='how-we-assess-your-project',
    ),
    path(
        'what-we-offer-you/',
        skip_ga360(
            TemplateView.as_view(
                template_name='domestic/ukef/what_we_offer.html',
            )
        ),
        name='what-we-offer-you',
    ),
    path(
        'country-cover/',
        skip_ga360(
            TemplateView.as_view(
                template_name='domestic/ukef/country_cover.html',
            )
        ),
        name='country-cover',
    ),
    path(
        'uk-export-contact-form/',
        skip_ga360(domestic.views.ukef.ContactView.as_view()),
        {'slug': 'uk-export-contact'},
        name='uk-export-contact',
    ),
    path(
        'uk-export-contact-form-success/',
        skip_ga360(domestic.views.ukef.SuccessPageView.as_view()),
        name='uk-export-contact-success',
    ),
]
