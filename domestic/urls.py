from django.urls import path
from django.views.generic import TemplateView
from great_components.decorators import skip_ga360

import domestic.views.euexit
import domestic.views.marketaccess
import domestic.views.ukef
from core import snippet_slugs

app_name = 'domestic'

# WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD THE URL NAME
# TO core.views.StaticViewSitemap.items()
urlpatterns = [
    path(
        'get-finance/',
        skip_ga360(domestic.views.ukef.UKEFHomeView.as_view()),
        name='get-finance',
    ),
    path(
        'get-finance/<slug:step>/',
        skip_ga360(
            domestic.views.ukef.GetFinanceLeadGenerationFormView.as_view(
                url_name='domestic:uk-export-finance-lead-generation-form',
                done_step_name='finished',
            )
        ),
        name='uk-export-finance-lead-generation-form',
    ),
    path(
        'get-finance/contact/thanks/',
        skip_ga360(
            TemplateView.as_view(
                template_name='domestic/finance/lead_generation_form/success.html',
            )
        ),
        name='uk-export-finance-lead-generation-form-success',
    ),
    # 'trade-finance/' is added via CMS as a TradeFinancePage with the slug 'trade-finance'
    path(
        'project-finance/',
        skip_ga360(
            TemplateView.as_view(
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
    path(
        'transition-period/contact/',
        domestic.views.euexit.DomesticContactFormView.as_view(),
        {
            'slug': snippet_slugs.EUEXIT_DOMESTIC_FORM,
            'snippet_import_path': 'contact.models.ContactPageContentSnippet',
            # see core.mixins.GetSnippetContentMixin
        },
        name='brexit-contact-form',
    ),
    path(
        'transition-period/contact/success/',
        domestic.views.euexit.DomesticContactSuccessView.as_view(),
        {
            'slug': snippet_slugs.EUEXIT_FORM_SUCCESS,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',
            # see core.mixins.GetSnippetContentMixin
        },
        name='brexit-contact-form-success',
    ),
    path(
        'report-trade-barrier/',
        skip_ga360(
            domestic.views.marketaccess.MarketAccessView.as_view(),
        ),
        name='market-access',
    ),
    path(
        'report-trade-barrier/report/success/',
        skip_ga360(
            domestic.views.marketaccess.ReportMarketAccessBarrierSuccessView.as_view(),
        ),
        name='report-barrier-form-success',
    ),
    path(
        'report-trade-barrier/report/<slug:step>/',
        skip_ga360(
            domestic.views.marketaccess.ReportMarketAccessBarrierFormView.as_view(
                url_name='domestic:report-ma-barrier',
                done_step_name='finished',
            )
        ),
        name='report-ma-barrier',
    ),
]
