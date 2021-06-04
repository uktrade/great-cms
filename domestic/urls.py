from django.urls import path
from django.views.generic import TemplateView
from great_components.decorators import skip_ga360

import domestic.views.ukef

app_name = 'domestic'

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
]
