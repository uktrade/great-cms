from functools import partial
from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls import url
from django.views.generic.base import RedirectView

from core.cms_slugs import PRIVACY_POLICY_URL, TERMS_URL
from core.views import (
    OpportunitiesRedirectView,
    QuerystringRedirectView,
    TranslationRedirectView,
)

build_great_international_url = partial(urljoin, '/international/')


redirects = [
    url(
        r'^about/$',
        QuerystringRedirectView.as_view(
            url='https://www.gov.uk/government/organisations/department-for-international-trade/about-our-services'
        ),
        name='events-about-legacy',
    ),
    url(
        r'^jpm/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/ehome/200197163/'),
        name='JPM-fintech-nov-2019',
    ),
    url(r'^brexit/$', QuerystringRedirectView.as_view(url='/transition/'), name='brexit-redirect'),
    url(
        r'^transition/$',
        QuerystringRedirectView.as_view(url='/international/content/invest/how-to-setup-in-the-uk/transition-period/'),
        name='transition-redirect',
    ),
    url(
        r'^eu-exit-news/contact/$',
        QuerystringRedirectView.as_view(
            url='/transition-period/contact/'
        ),  # TODO: update to named url when we have migrated it
        name='eu-exit-brexit-contact-redirect',
    ),
    url(
        r'^eu-exit-news/contact/success/$',
        QuerystringRedirectView.as_view(
            url='/transition-period/contact/success/'
        ),  # TODO: update to named url when we have migrated it
        name='eu-exit-brexit-contact-success-redirect',
    ),
    url(
        r'^redarrows/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/red-arrows-north-america-tour/'),
        name='redarrows-redirect',
    ),
    url(
        r'^new-zealand-event-calendar/$',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=zealand'
        ),
        name='new-zealand-redirect',
    ),
    url(
        r'^story/online-marketplaces-propel-freestyle-xtreme-sales/$',
        QuerystringRedirectView.as_view(url='/'),
        name='casestudy-online-marketplaces',
    ),
    url(
        r'^australia-event-calendar/$',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=australia'
        ),
        name='australia-event-calendar',
    ),
    url(
        r'^trskorea/$(?i)',
        QuerystringRedirectView.as_view(url='https://eu.eventscloud.com/korea-uk-tech-rocketship-awards-kr'),
    ),
    url(r'^ukti/$(?i)', QuerystringRedirectView.as_view(url='/')),
    url(
        r'^future/$',
        QuerystringRedirectView.as_view(
            url=('https://www.events.great.gov.uk/ehome/index.php?' 'eventid=200185206'),
        ),
    ),
    url(
        r'^innovation-hk/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-hk',
        ),
    ),
    url(
        r'^innovation-china/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-china',
        ),
    ),
    url(
        r'^innovation-asean/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-asean',
        ),
    ),
    url(
        r'^innovation-au-nz/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-au-nz',
        ),
    ),
    url(
        r'^innovation-jpn/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-jpn',
        ),
    ),
    url(
        r'^innovation-kor/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-kor',
        ),
    ),
    url(
        r'^bodw2019/$(?i)',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/bodw2019/'),
    ),
    url(
        r'^events/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/'),
    ),
    url(
        r'^expo2020/$',
        RedirectView.as_view(url='https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ),
    url(
        r'^ukpavilion2020/$',
        RedirectView.as_view(url='https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ),
    url(
        r'^beijingexpo2019/$(?i)',
        RedirectView.as_view(url='https://www.events.great.gov.uk/ehome/index.php?eventid=200188985&'),  # NOQA
    ),
    url(
        r'^exporting-edge/$',
        RedirectView.as_view(url='/get-finance/'),
        # TODO: move back to pattern_name='get-finance' when it's migrated
    ),
    url(
        r'^invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^int/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^us/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^es/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=es'),
    ),
    url(
        r'^int/es/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=es',
        ),
    ),
    url(
        r'^cn/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=zh-hans'),
    ),
    url(
        r'^int/zh/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=zh-hans',
        ),
    ),
    url(
        r'^int/pt/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=pt',
        ),
    ),
    url(
        r'^br/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^de/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=de'),
    ),
    url(
        r'^int/de/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=de',
        ),
    ),
    url(
        r'^jp/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=ja'),
    ),
    url(
        r'^int/ja/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=ja',
        ),
    ),
    url(
        r'^in/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^int/ar/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    url(
        r'^study/$',
        QuerystringRedirectView.as_view(
            url='https://study-uk.britishcouncil.org',
        ),
    ),
    url(
        r'^visit/$',
        QuerystringRedirectView.as_view(
            url='https://www.visitbritain.com/gb/en',
        ),
    ),
    url(
        r'^export/$',
        QuerystringRedirectView.as_view(url='/'),
    ),
    url(
        r'^export/new/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    url(
        r'^export/occasional/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    url(
        r'^export/regular/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    url(
        r'^export/opportunities/$',
        QuerystringRedirectView.as_view(
            url='/export-opportunities/',
        ),
    ),
    url(
        r'^opportunities/$',
        QuerystringRedirectView.as_view(
            url='/export-opportunities/',
        ),
    ),
    url(
        r'^opportunities/(?P<slug>[-\w]+)/$',
        # Redirects to /export-opportunities/
        # with the slug and query parameters
        OpportunitiesRedirectView.as_view(),
    ),
    url(
        r'^export/find-a-buyer/$',
        QuerystringRedirectView.as_view(
            url='/find-a-buyer/',
        ),
    ),
    url(
        r'^export/selling-online-overseas/$',
        QuerystringRedirectView.as_view(
            url='/selling-online-overseas/',
        ),
    ),
    url(
        r'^uk/privacy-policy/$',
        QuerystringRedirectView.as_view(url=PRIVACY_POLICY_URL),
    ),
    url(
        r'^uk/terms-and-conditions/$',
        QuerystringRedirectView.as_view(url=TERMS_URL),
    ),
    url(
        r'^uk/$',
        TranslationRedirectView.as_view(url='/'),
    ),
    url(
        r'^int/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    url(
        r'^in/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    url(
        r'^us/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    url(
        r'^innovation/$',
        QuerystringRedirectView.as_view(
            url=('https://www.events.trade.gov.uk/' 'the-great-festival-of-innovation-hong-kong-2018/'),
        ),
    ),
    url(
        r'^uk/cy/$',
        QuerystringRedirectView.as_view(
            url=('https://www.great.gov.uk/?utm_source=Mailing&utm_medium' '=Brochure&utm_campaign=ExportBrochureCY'),
        ),
    ),
    url(
        r'^verify/$',
        QuerystringRedirectView.as_view(
            url=('/find-a-buyer/verify/letter-confirm/'),
        ),
    ),
    url(
        r'^legal/$',
        QuerystringRedirectView.as_view(
            url='/international/content/industries/legal-services/',
        ),
    ),
    url(
        r'^kr/$',
        QuerystringRedirectView.as_view(
            url=(
                'https://www.events.trade.gov.uk/invest-in-great---korea'
                '?utm_source=print&utm_campaign=korean_winter_olympics_invest'
            )
        ),
    ),
    url(
        r'^local-export-support/apply/$',
        QuerystringRedirectView.as_view(
            url='/contact/export-advice/business/',
        ),
    ),
    url(
        r'^companion/$',
        QuerystringRedirectView.as_view(
            url='https://digital-companion.ava-digi.de/'),
        name='companion'
    ),
]

if settings.FEATURE_FLAG_INTERNATIONAL_CONTACT_TRIAGE_ENABLED:
    redirects += [
        url(
            r'^contact/triage/international/$',
            QuerystringRedirectView.as_view(url='/international/contact/'),
            name='contact-triage-redirect',
        ),
    ]

# (<lang code path>, <language to use in query parameter>)
INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING = [
    ('de', 'de'),
    ('ar', 'ar'),
    ('zh', 'zh-hans'),
    ('pt', 'pt'),
    ('es', 'es'),
    ('ja', 'ja'),
]

international_redirects = [
    url(r'^today/$', QuerystringRedirectView.as_view(url='/international/content/capital-invest/'))
]

international_redirects += [
    url(
        r'^int/{path}/$'.format(path=redirect[0]),
        TranslationRedirectView.as_view(
            url='/international/',
            language=redirect[1],
        ),
    )
    for redirect in INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING
]
# (<country code path>, <language to use in query parameter>)
INTERNATIONAL_COUNTRY_REDIRECTS_MAPPING = [
    ('cn', 'zh-hans'),
    ('br', 'pt'),
    ('jp', 'ja'),
]
international_redirects += [
    url(
        r'^{path}/$'.format(path=redirect[0]),
        TranslationRedirectView.as_view(
            url='/international/',
            language=redirect[1],
        ),
    )
    for redirect in (INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING + INTERNATIONAL_COUNTRY_REDIRECTS_MAPPING)
]

# TOS and privacy-and-cookies are no longer translated, instead we redirect to
# the ENG version
TOS_AND_PRIVACY_REDIRECT_LANGUAGES = ('zh', 'ja', 'es', 'pt', 'ar', 'de')

tos_redirects = [
    url(
        r'^int/{path}/terms-and-conditions/$'.format(path=language),
        QuerystringRedirectView.as_view(
            url=TERMS_URL,
        ),
    )
    for language in TOS_AND_PRIVACY_REDIRECT_LANGUAGES
]

privacy_redirects = [
    url(
        r'^int/{path}/privacy-policy/$'.format(path=language),
        QuerystringRedirectView.as_view(
            url=PRIVACY_POLICY_URL,
        ),
    )
    for language in TOS_AND_PRIVACY_REDIRECT_LANGUAGES
]

# TODO: once the contact app has been migrated from v1 into v2, we can
# swap the following hard-coded URLs back to reverse_lazy

# /contact/feedback/ -> reverse_lazy('contact-us-feedback')
# /contact/triage/great-account/ -> reverse_lazy('contact-us-routing-form', kwargs={'step': 'great-account'})
# /contact/triage/domestic/ -> reverse_lazy('contact-us-routing-form', kwargs={'step': 'domestic'})
# /contact/triage/location/ -> reverse_lazy('contact-us-routing-form', kwargs={'step': 'location'})
contact_redirects = [
    url(
        r'^legacy/contact/(?P<service>[-\w\d]+)/FeedbackForm/$',
        QuerystringRedirectView.as_view(url='/contact/feedback/'),
    ),
    url(
        r'^legacy/contact/feedback/(?P<service>[-\w\d]+)/$',
        QuerystringRedirectView.as_view(url='/contact/feedback/'),
    ),
    url(
        r'^legacy/contact/feedback/$',
        QuerystringRedirectView.as_view(url='/contact/feedback/'),
    ),
    url(
        r'^legacy/contact/(?P<service>[-\w\d]+)/feedback/$',
        QuerystringRedirectView.as_view(url='/contact/feedback/'),
    ),
    url(
        r'^legacy/contact/single_sign_on/$',
        QuerystringRedirectView.as_view(url='/contact/triage/great-account/'),
    ),
    url(
        r'^legacy/contact/selling_online_overseas/$',
        QuerystringRedirectView.as_view(url='/contact/triage/domestic/'),
    ),
    url(
        r'^legacy/contact/export_ops/$',
        QuerystringRedirectView.as_view(url='/contact/triage/domestic/'),
    ),
    url(
        r'^legacy/contact/export_opportunities/$',
        QuerystringRedirectView.as_view(url='/contact/triage/domestic/'),
    ),
    url(
        r'^legacy/contact/cookies/$',
        QuerystringRedirectView.as_view(url=PRIVACY_POLICY_URL),
    ),
    url(
        r'^legacy/contact/terms-and-conditions/$',
        QuerystringRedirectView.as_view(url=TERMS_URL),
    ),
    # catch everything not covered above but not interfere with trailing slash
    # redirects
    url(
        r'^legacy/contact/(.*/)?$',
        QuerystringRedirectView.as_view(url='/contact/triage/location/'),
    ),
    url(
        r'^brexit/contact/$',
        QuerystringRedirectView.as_view(url='/transition-period/contact/'),
        # TODO: move back to reverse_lazy('brexit-contact-form') when migrated
    ),
    url(
        r'^brexit/contact/success/$',
        QuerystringRedirectView.as_view(url='/transition-period/contact/success/'),
        # TODO: move back to reverse_lazy('brexit-contact-form-success') when migrated
    ),
]

articles_redirects = [
    url(r'^market-research/$', QuerystringRedirectView.as_view(url='/advice/find-an-export-market/')),
    url(
        r'^market-research/do-research-first/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/plan-export-market-research/'),
    ),
    url(
        r'^market-research/define-market-potential/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/define-export-market-potential/'),
    ),
    url(
        r'^market-research/analyse-the-competition/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/define-export-market-potential/'),
    ),
    url(
        r'^market-research/research-your-market/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/field-research-in-export-markets/'),
    ),
    url(
        r'^market-research/visit-a-trade-show/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/trade-shows/'),
    ),
    url(
        r'^market-research/doing-business-with-integrity/$',
        QuerystringRedirectView.as_view(
            url='advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/'
        ),
    ),
    url(
        r'^market-research/know-the-relevant-legislation/$',
        QuerystringRedirectView.as_view(
            url='advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/'
        ),
    ),
    url(r'^business-planning/$', QuerystringRedirectView.as_view(url='/advice/define-route-to-market/')),
    url(
        r'^business-planning/make-an-export-plan/$',
        QuerystringRedirectView.as_view(url='/advice/create-an-export-plan/how-to-create-an-export-plan/'),
    ),
    url(
        r'^business-planning/find-a-route-to-market/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/routes-to-market/'),
    ),
    url(
        r'^business-planning/sell-overseas-directly/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/sell-overseas-directly/'),
    ),
    url(
        r'^business-planning/use-an-overseas-agent/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-agents/'),
    ),
    url(
        r'^business-planning/choosing-an-agent-or-distributor/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-agents/'),
    ),
    url(
        r'^business-planning/use-a-distributor/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-distributors/'),
    ),
    url(
        r'^business-planning/license-your-product-or-service/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-licensing-agreement/'),
    ),
    url(
        r'^business-planning/licensing-and-franchising/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-licensing-agreement/'),
    ),
    url(
        r'^business-planning/franchise-your-business/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-franchise-agreement/'),
    ),
    url(
        r'^business-planning/start-a-joint-venture/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-joint-venture-agreement/'),
    ),
    url(
        r'^business-planning/set-up-an-overseas-operation/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/set-up-a-business-abroad/'),
    ),
    url(r'^finance/$', QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/')),
    url(
        r'^finance/choose-the-right-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/choose-the-right-finance/'),
    ),
    url(
        r'^finance/get-money-to-export/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/choose-the-right-finance/'),
    ),
    url(
        r'^finance/get-export-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    url(
        r'^finance/get-finance-support-from-government/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    url(
        r'^finance/raise-money-by-borrowing/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/raise-money-by-borrowing/'),
    ),
    url(
        r'^finance/borrow-against-assets/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/borrow-against-assets/'),
    ),
    url(
        r'^finance/raise-money-with-investment/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/raise-money-with-investment/'),
    ),
    url(
        r'^getting-paid/invoice-currency-and-contents/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/payment-methods-for-exporters/'),
    ),
    url(
        r'^getting-paid/consider-how-to-get-paid/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-payment-for-export-orders/how-to-create-an-export-invoice/'
        ),
    ),
    url(
        r'^getting-paid/decide-when-to-get-paid/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-payment-for-export-orders/decide-when-to-get-paid-for-export-orders/'
        ),
    ),
    url(
        r'^getting-paid/payment-methods/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/payment-methods-for-exporters/'),
    ),
    url(
        r'^getting-paid/insure-against-non-payment/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/insure-against-non-payment/'),
    ),
    url(r'^getting-paid/$', QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/')),
    url(
        r'^customer-insight/$',
        QuerystringRedirectView.as_view(url='/advice/prepare-to-do-business-in-a-foreign-country/'),
    ),
    url(
        r'^customer-insight/meet-your-customers/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    url(
        r'^customer-insight/know-your-customers/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/understand-business-risk-in-overseas-markets/'
        ),
    ),
    url(
        r'^customer-insight/manage-language-differences/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    url(
        r'^customer-insight/understand-your-customers-culture/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    url(
        r'^operations-and-compliance/$',
        QuerystringRedirectView.as_view(url='/advice/manage-legal-and-ethical-compliance/'),
    ),
    url(
        r'^operations-and-compliance/internationalise-your-website/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/'
        ),
    ),
    url(
        r'^operations-and-compliance/match-your-website-to-your-audience/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/'
        ),
    ),
    url(
        r'^operations-and-compliance/protect-your-intellectual-property/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    url(
        r'^operations-and-compliance/types-of-intellectual-property/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    url(
        r'^operations-and-compliance/know-what-ip-you-have/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    url(
        r'^operations-and-compliance/international-ip-protection/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    url(
        r'^operations-and-compliance/report-corruption/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/report-corruption-and-human-rights-violations/'
        ),
    ),
    url(
        r'^operations-and-compliance/anti-bribery-and-corruption-training/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/anti-bribery-and-corruption-training/'
        ),
    ),
    url(
        r'^operations-and-compliance/plan-the-logistics/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/plan-logistics-for-exporting/'
        ),
    ),
    url(
        r'^operations-and-compliance/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/'
        ),
    ),
    url(
        r'^operations-and-compliance/use-a-freight-forwarder/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/use-a-freight-forwarder-to-export/'
        ),
    ),
    url(
        r'^operations-and-compliance/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/use-incoterms-in-contracts/'
        ),
    ),
    url(r'^new/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    url(r'^occasional/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    url(r'^regular/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    url(r'^new/$', QuerystringRedirectView.as_view(url='/advice/')),
    url(r'^occasional/$', QuerystringRedirectView.as_view(url='/advice/')),
    url(r'^regular/$', QuerystringRedirectView.as_view(url='/advice/')),
    # CMS-1410 redirects for updated 'export advice' articles
    url(
        r'^advice/find-an-export-market/plan-export-market-research/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/understand-export-market-research/'),
    ),
    url(
        r'^advice/find-an-export-market/define-export-market-potential/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/research-export-markets-online/'),
    ),
    url(
        r'^advice/find-an-export-market/field-research-in-export-markets/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/research-in-market/'),
    ),
    url(
        r'^advice/get-export-finance-and-funding/choose-the-right-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/understand-export-finance/'),
    ),
    url(
        r'^advice/get-export-finance-and-funding/raise-money-by-borrowing/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    url(
        r'^advice/get-export-finance-and-funding/borrow-against-assets/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    url(
        r'^advice/get-export-finance-and-funding/raise-money-with-investment/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    url(
        r'^advice/use-a-freight-forwarder-to-export/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    url(
        r'^advice/prepare-for-export-procedures-and-logistics/use-a-freight-forwarder-to-export/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    url(
        r'^advice/plan-logistics-for-exporting/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    url(
        r'^advice/prepare-for-export-procedures-and-logistics/plan-logistics-for-exporting/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    url(
        r'^advice/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/'
        ),
    ),
    url(
        r'^advice/prepare-for-export-procedures-and-logistics/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/'
        ),
    ),
    url(
        r'^advice/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/documentation-international-trade/'
        ),
    ),
    url(
        r'^advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/documentation-international-trade/'
        ),
    ),
    url(
        r'^trade/$',
        QuerystringRedirectView.as_view(url='/international/trade/'),
        name='international-trade-home',
    ),
    url(
        r'^trade/(?P<path>[\w\-/]*)/$',
        QuerystringRedirectView.as_view(
            url=build_great_international_url('trade/incoming/%(path)s/'),
            # Note that this then has a FURTHER redirect within great-international-ui
        ),
        name='international-trade',
    ),
    url(
        r'^investment-support-directory/$',
        QuerystringRedirectView.as_view(url='/international/investment-support-directory/'),
        name='international-investment-support-directory-home',
    ),
    url(
        r'^investment-support-directory/(?P<path>[\w\-/]*)/$',
        QuerystringRedirectView.as_view(
            url=build_great_international_url('investment-support-directory/%(path)s/'),
            # Note that this then has a FURTHER redirect within great-international-ui
        ),
        name='international-investment-support-directory',
    ),
    url(
        r'^story/york-bag-retailer-goes-global-via-e-commerce/$',
        QuerystringRedirectView.as_view(url='/success-stories/york-bag-retailer-goes-global/'),
    ),
    url(
        r'^story/hello-babys-rapid-online-growth/$',
        QuerystringRedirectView.as_view(url='/success-stories/hello-babys-rapid-online-growth/'),
    ),
]


redirects += tos_redirects + contact_redirects + privacy_redirects + international_redirects + articles_redirects
