from django.urls import include, path
from great_components.decorators import skip_ga360

import domestic.views.marketaccess
import domestic.views.ukef
from domestic.views.campaign import CampaignView

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
            # if not settings.FEATURE_DIGITAL_POINT_OF_ENTRY
            # else QuerystringRedirectView.as_view(url=DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE)
        ),
        name='uk-export-finance-lead-generation-form',
    ),
    path(
        'get-finance/contact/thanks/',
        skip_ga360(domestic.views.ukef.ThanksView.as_view()),
        name='uk-export-finance-lead-generation-form-success',
    ),
    path(
        'project-finance/',
        skip_ga360(domestic.views.ukef.UKEFProjectFinanceView.as_view()),
        name='project-finance',
    ),
    path(
        'how-we-assess-your-project/',
        skip_ga360(domestic.views.ukef.UKEFHowWeAssessView.as_view()),
        name='how-we-assess-your-project',
    ),
    path(
        'what-we-offer-you/',
        skip_ga360(domestic.views.ukef.UKEFWhatWeOfferView.as_view()),
        name='what-we-offer-you',
    ),
    path(
        'country-cover/',
        skip_ga360(domestic.views.ukef.UKEFCountryCoverView.as_view()),
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
    path(
        'campaigns/<slug:page_slug>/',
        skip_ga360(CampaignView.as_view()),
        name='campaigns',
    ),
    path('', include('bgs_chat.urls')),
]
