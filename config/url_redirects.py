from functools import partial
from urllib.parse import urljoin

from django.urls import re_path, reverse_lazy
from django.views.generic.base import RedirectView

from core.cms_slugs import PRIVACY_POLICY_URL, TERMS_URL
from core.views import (
    OpportunitiesRedirectView,
    QuerystringRedirectView,
    TranslationRedirectView,
)

build_great_international_url = partial(urljoin, '/international/')


redirects = [
    re_path(
        r'^about/$',
        QuerystringRedirectView.as_view(
            url='https://www.gov.uk/government/organisations/department-for-international-trade/about-our-services'
        ),
        name='events-about-legacy',
    ),
    re_path(
        r'^jpm/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/ehome/200197163/'),
        name='JPM-fintech-nov-2019',
    ),
    re_path(r'^brexit/$', QuerystringRedirectView.as_view(url='/transition/'), name='brexit-redirect'),
    re_path(
        r'^transition/$',
        QuerystringRedirectView.as_view(url='/international/content/invest/how-to-setup-in-the-uk/transition-period/'),
        name='transition-redirect',
    ),
    re_path(
        r'^redarrows/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/red-arrows-north-america-tour/'),
        name='redarrows-redirect',
    ),
    re_path(
        r'^new-zealand-event-calendar/$',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=zealand'
        ),
        name='new-zealand-redirect',
    ),
    re_path(
        r'^story/online-marketplaces-propel-freestyle-xtreme-sales/$',
        QuerystringRedirectView.as_view(url='/'),
        name='casestudy-online-marketplaces',
    ),
    re_path(
        r'^australia-event-calendar/$',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=australia'
        ),
        name='australia-event-calendar',
    ),
    re_path(
        r'^trskorea/$(?i)',
        QuerystringRedirectView.as_view(url='https://eu.eventscloud.com/korea-uk-tech-rocketship-awards-kr'),
    ),
    re_path(r'^ukti/$(?i)', QuerystringRedirectView.as_view(url='/')),
    re_path(
        r'^future/$',
        QuerystringRedirectView.as_view(
            url=('https://www.events.great.gov.uk/ehome/index.php?' 'eventid=200185206'),
        ),
    ),
    re_path(
        r'^innovation-hk/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-hk',
        ),
    ),
    re_path(
        r'^innovation-china/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-china',
        ),
    ),
    re_path(
        r'^innovation-asean/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-asean',
        ),
    ),
    re_path(
        r'^innovation-au-nz/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-au-nz',
        ),
    ),
    re_path(
        r'^innovation-jpn/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-jpn',
        ),
    ),
    re_path(
        r'^innovation-kor/$(?i)',
        QuerystringRedirectView.as_view(
            url='https://www.events.great.gov.uk/ehome/innovation-kor',
        ),
    ),
    re_path(
        r'^bodw2019/$(?i)',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/bodw2019/'),
    ),
    re_path(
        r'^events/$',
        QuerystringRedirectView.as_view(url='https://www.events.great.gov.uk/'),
    ),
    re_path(
        r'^expo2020/$',
        RedirectView.as_view(url='https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ),
    re_path(
        r'^ukpavilion2020/$',
        RedirectView.as_view(url='https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ),
    re_path(
        r'^beijingexpo2019/$(?i)',
        RedirectView.as_view(url='https://www.events.great.gov.uk/ehome/index.php?eventid=200188985&'),  # NOQA
    ),
    re_path(
        r'^exporting-edge/$',
        RedirectView.as_view(pattern_name='domestic:get-finance'),
    ),
    re_path(
        r'^invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^int/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^us/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^es/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=es'),
    ),
    re_path(
        r'^int/es/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=es',
        ),
    ),
    re_path(
        r'^cn/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=zh-hans'),
    ),
    re_path(
        r'^int/zh/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=zh-hans',
        ),
    ),
    re_path(
        r'^int/pt/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=pt',
        ),
    ),
    re_path(
        r'^br/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^de/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=de'),
    ),
    re_path(
        r'^int/de/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=de',
        ),
    ),
    re_path(
        r'^jp/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest?lang=ja'),
    ),
    re_path(
        r'^int/ja/invest/$',
        QuerystringRedirectView.as_view(
            url='/international/invest?lang=ja',
        ),
    ),
    re_path(
        r'^in/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^int/ar/invest/$',
        QuerystringRedirectView.as_view(url='/international/invest'),
    ),
    re_path(
        r'^study/$',
        QuerystringRedirectView.as_view(
            url='https://study-uk.britishcouncil.org',
        ),
    ),
    re_path(
        r'^visit/$',
        QuerystringRedirectView.as_view(
            url='https://www.visitbritain.com/gb/en',
        ),
    ),
    re_path(
        r'^export/$',
        QuerystringRedirectView.as_view(url='/'),
    ),
    re_path(
        r'^export/new/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    re_path(
        r'^export/occasional/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    re_path(
        r'^export/regular/$',
        QuerystringRedirectView.as_view(
            url='/advice/',
        ),
    ),
    re_path(
        r'^export/opportunities/$',
        QuerystringRedirectView.as_view(
            url='/export-opportunities/',
        ),
    ),
    re_path(
        r'^opportunities/$',
        QuerystringRedirectView.as_view(
            url='/export-opportunities/',
        ),
    ),
    re_path(
        r'^opportunities/(?P<slug>[-\w]+)/$',
        # Redirects to /export-opportunities/
        # with the slug and query parameters
        OpportunitiesRedirectView.as_view(),
    ),
    re_path(
        r'^export/find-a-buyer/$',
        QuerystringRedirectView.as_view(
            url='/find-a-buyer/',
        ),
    ),
    re_path(
        r'^export/selling-online-overseas/$',
        QuerystringRedirectView.as_view(
            url='/selling-online-overseas/',
        ),
    ),
    re_path(
        r'^uk/privacy-policy/$',
        QuerystringRedirectView.as_view(url=PRIVACY_POLICY_URL),
    ),
    re_path(
        r'^uk/terms-and-conditions/$',
        QuerystringRedirectView.as_view(url=TERMS_URL),
    ),
    re_path(
        r'^uk/$',
        TranslationRedirectView.as_view(url='/'),
    ),
    re_path(
        r'^int/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    re_path(
        r'^in/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    re_path(
        r'^us/$',
        TranslationRedirectView.as_view(url='/international/'),
    ),
    re_path(
        r'^innovation/$',
        QuerystringRedirectView.as_view(
            url=('https://www.events.trade.gov.uk/' 'the-great-festival-of-innovation-hong-kong-2018/'),
        ),
    ),
    re_path(
        r'^uk/cy/$',
        QuerystringRedirectView.as_view(
            url=('https://www.great.gov.uk/?utm_source=Mailing&utm_medium' '=Brochure&utm_campaign=ExportBrochureCY'),
        ),
    ),
    re_path(
        r'^verify/$',
        QuerystringRedirectView.as_view(
            url=('/find-a-buyer/verify/letter-confirm/'),
        ),
    ),
    re_path(
        r'^legal/$',
        QuerystringRedirectView.as_view(
            url='/international/content/industries/legal-services/',
        ),
    ),
    re_path(
        r'^kr/$',
        QuerystringRedirectView.as_view(
            url=(
                'https://www.events.trade.gov.uk/invest-in-great---korea'
                '?utm_source=print&utm_campaign=korean_winter_olympics_invest'
            )
        ),
    ),
    re_path(
        r'^local-export-support/apply/$',
        QuerystringRedirectView.as_view(
            url='/contact/export-advice/business/',
        ),
    ),
    re_path(
        r'^companion/$', QuerystringRedirectView.as_view(url='https://digital-companion.ava-digi.de/'), name='companion'
    ),
]

redirects += [
    re_path(
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
    re_path(r'^today/$', QuerystringRedirectView.as_view(url='/international/content/capital-invest/'))
]

international_redirects += [
    re_path(
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
    re_path(
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
    re_path(
        r'^int/{path}/terms-and-conditions/$'.format(path=language),
        QuerystringRedirectView.as_view(
            url=TERMS_URL,
        ),
    )
    for language in TOS_AND_PRIVACY_REDIRECT_LANGUAGES
]

privacy_redirects = [
    re_path(
        r'^int/{path}/privacy-policy/$'.format(path=language),
        QuerystringRedirectView.as_view(
            url=PRIVACY_POLICY_URL,
        ),
    )
    for language in TOS_AND_PRIVACY_REDIRECT_LANGUAGES
]

contact_redirects = [
    re_path(
        r'^legacy/contact/(?P<service>[-\w\d]+)/FeedbackForm/$',
        QuerystringRedirectView.as_view(url=reverse_lazy('contact:contact-us-feedback')),
    ),
    re_path(
        r'^legacy/contact/feedback/(?P<service>[-\w\d]+)/$',
        QuerystringRedirectView.as_view(url=reverse_lazy('contact:contact-us-feedback')),
    ),
    re_path(
        r'^legacy/contact/feedback/$',
        QuerystringRedirectView.as_view(url=reverse_lazy('contact:contact-us-feedback')),
    ),
    re_path(
        r'^legacy/contact/(?P<service>[-\w\d]+)/feedback/$',
        QuerystringRedirectView.as_view(url=reverse_lazy('contact:contact-us-feedback')),
    ),
    re_path(
        r'^legacy/contact/single_sign_on/$',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'great-account'},
            )
        ),
    ),
    re_path(
        r'^legacy/contact/selling_online_overseas/$',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'domestic'},
            )
        ),
    ),
    re_path(
        r'^legacy/contact/export_ops/$',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'domestic'},
            )
        ),
    ),
    re_path(
        r'^legacy/contact/export_opportunities/$',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'domestic'},
            )
        ),
    ),
    re_path(
        r'^legacy/contact/cookies/$',
        QuerystringRedirectView.as_view(url=PRIVACY_POLICY_URL),
    ),
    re_path(
        r'^legacy/contact/terms-and-conditions/$',
        QuerystringRedirectView.as_view(url=TERMS_URL),
    ),
    # catch everything not covered above but not interfere with trailing slash
    # redirects
    re_path(
        r'^legacy/contact/(.*/)?$',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'location'},
            )
        ),
    ),
]

articles_redirects = [
    re_path(r'^market-research/$', QuerystringRedirectView.as_view(url='/advice/find-an-export-market/')),
    re_path(
        r'^market-research/do-research-first/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/plan-export-market-research/'),
    ),
    re_path(
        r'^market-research/define-market-potential/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/define-export-market-potential/'),
    ),
    re_path(
        r'^market-research/analyse-the-competition/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/define-export-market-potential/'),
    ),
    re_path(
        r'^market-research/research-your-market/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/field-research-in-export-markets/'),
    ),
    re_path(
        r'^market-research/visit-a-trade-show/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/trade-shows/'),
    ),
    re_path(
        r'^market-research/doing-business-with-integrity/$',
        QuerystringRedirectView.as_view(
            url='advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/'
        ),
    ),
    re_path(
        r'^market-research/know-the-relevant-legislation/$',
        QuerystringRedirectView.as_view(
            url='advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/'
        ),
    ),
    re_path(r'^business-planning/$', QuerystringRedirectView.as_view(url='/advice/define-route-to-market/')),
    re_path(
        r'^business-planning/make-an-export-plan/$',
        QuerystringRedirectView.as_view(url='/advice/create-an-export-plan/how-to-create-an-export-plan/'),
    ),
    re_path(
        r'^business-planning/find-a-route-to-market/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/routes-to-market/'),
    ),
    re_path(
        r'^business-planning/sell-overseas-directly/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/sell-overseas-directly/'),
    ),
    re_path(
        r'^business-planning/use-an-overseas-agent/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-agents/'),
    ),
    re_path(
        r'^business-planning/choosing-an-agent-or-distributor/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-agents/'),
    ),
    re_path(
        r'^business-planning/use-a-distributor/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/export-distributors/'),
    ),
    re_path(
        r'^business-planning/license-your-product-or-service/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-licensing-agreement/'),
    ),
    re_path(
        r'^business-planning/licensing-and-franchising/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-licensing-agreement/'),
    ),
    re_path(
        r'^business-planning/franchise-your-business/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-franchise-agreement/'),
    ),
    re_path(
        r'^business-planning/start-a-joint-venture/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/create-a-joint-venture-agreement/'),
    ),
    re_path(
        r'^business-planning/set-up-an-overseas-operation/$',
        QuerystringRedirectView.as_view(url='/advice/define-route-to-market/set-up-a-business-abroad/'),
    ),
    re_path(r'^finance/$', QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/')),
    re_path(
        r'^finance/choose-the-right-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/choose-the-right-finance/'),
    ),
    re_path(
        r'^finance/get-money-to-export/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/choose-the-right-finance/'),
    ),
    re_path(
        r'^finance/get-export-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    re_path(
        r'^finance/get-finance-support-from-government/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    re_path(
        r'^finance/raise-money-by-borrowing/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/raise-money-by-borrowing/'),
    ),
    re_path(
        r'^finance/borrow-against-assets/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/borrow-against-assets/'),
    ),
    re_path(
        r'^finance/raise-money-with-investment/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/raise-money-with-investment/'),
    ),
    re_path(
        r'^getting-paid/invoice-currency-and-contents/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/payment-methods-for-exporters/'),
    ),
    re_path(
        r'^getting-paid/consider-how-to-get-paid/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-payment-for-export-orders/how-to-create-an-export-invoice/'
        ),
    ),
    re_path(
        r'^getting-paid/decide-when-to-get-paid/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-payment-for-export-orders/decide-when-to-get-paid-for-export-orders/'
        ),
    ),
    re_path(
        r'^getting-paid/payment-methods/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/payment-methods-for-exporters/'),
    ),
    re_path(
        r'^getting-paid/insure-against-non-payment/$',
        QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/insure-against-non-payment/'),
    ),
    re_path(r'^getting-paid/$', QuerystringRedirectView.as_view(url='/advice/manage-payment-for-export-orders/')),
    re_path(
        r'^customer-insight/$',
        QuerystringRedirectView.as_view(url='/advice/prepare-to-do-business-in-a-foreign-country/'),
    ),
    re_path(
        r'^customer-insight/meet-your-customers/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    re_path(
        r'^customer-insight/know-your-customers/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/understand-business-risk-in-overseas-markets/'
        ),
    ),
    re_path(
        r'^customer-insight/manage-language-differences/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    re_path(
        r'^customer-insight/understand-your-customers-culture/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/$',
        QuerystringRedirectView.as_view(url='/advice/manage-legal-and-ethical-compliance/'),
    ),
    re_path(
        r'^operations-and-compliance/internationalise-your-website/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/match-your-website-to-your-audience/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/protect-your-intellectual-property/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/types-of-intellectual-property/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/know-what-ip-you-have/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/international-ip-protection/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/report-corruption/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/report-corruption-and-human-rights-violations/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/anti-bribery-and-corruption-training/$',
        QuerystringRedirectView.as_view(
            url='/advice/manage-legal-and-ethical-compliance/anti-bribery-and-corruption-training/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/plan-the-logistics/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/plan-logistics-for-exporting/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/use-a-freight-forwarder/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/use-a-freight-forwarder-to-export/'
        ),
    ),
    re_path(
        r'^operations-and-compliance/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/use-incoterms-in-contracts/'
        ),
    ),
    re_path(r'^new/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    re_path(r'^occasional/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    re_path(r'^regular/next-steps/$', QuerystringRedirectView.as_view(url='/advice/')),
    re_path(r'^new/$', QuerystringRedirectView.as_view(url='/advice/')),
    re_path(r'^occasional/$', QuerystringRedirectView.as_view(url='/advice/')),
    re_path(r'^regular/$', QuerystringRedirectView.as_view(url='/advice/')),
    # CMS-1410 redirects for updated 'export advice' articles
    re_path(
        r'^advice/find-an-export-market/plan-export-market-research/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/understand-export-market-research/'),
    ),
    re_path(
        r'^advice/find-an-export-market/define-export-market-potential/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/research-export-markets-online/'),
    ),
    re_path(
        r'^advice/find-an-export-market/field-research-in-export-markets/$',
        QuerystringRedirectView.as_view(url='/advice/find-an-export-market/research-in-market/'),
    ),
    re_path(
        r'^advice/get-export-finance-and-funding/choose-the-right-finance/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/understand-export-finance/'),
    ),
    re_path(
        r'^advice/get-export-finance-and-funding/raise-money-by-borrowing/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    re_path(
        r'^advice/get-export-finance-and-funding/borrow-against-assets/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    re_path(
        r'^advice/get-export-finance-and-funding/raise-money-with-investment/$',
        QuerystringRedirectView.as_view(url='/advice/get-export-finance-and-funding/get-export-finance/'),
    ),
    re_path(
        r'^advice/use-a-freight-forwarder-to-export/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    re_path(
        r'^advice/prepare-for-export-procedures-and-logistics/use-a-freight-forwarder-to-export/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    re_path(
        r'^advice/plan-logistics-for-exporting/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    re_path(
        r'^advice/prepare-for-export-procedures-and-logistics/plan-logistics-for-exporting/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/'
        ),
    ),
    re_path(
        r'^advice/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/'
        ),
    ),
    re_path(
        r'^advice/prepare-for-export-procedures-and-logistics/use-incoterms-in-contracts/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/'
        ),
    ),
    re_path(
        r'^advice/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/documentation-international-trade/'
        ),
    ),
    re_path(
        r'^advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/$',
        QuerystringRedirectView.as_view(
            url='/advice/prepare-for-export-procedures-and-logistics/documentation-international-trade/'
        ),
    ),
    re_path(
        r'^trade/$',
        QuerystringRedirectView.as_view(url='/international/trade/'),
        name='international-trade-home',
    ),
    re_path(
        r'^trade/(?P<path>[\w\-/]*)/$',
        QuerystringRedirectView.as_view(
            url=build_great_international_url('trade/incoming/%(path)s/'),
            # Note that this then has a FURTHER redirect within great-international-ui
        ),
        name='international-trade',
    ),
    re_path(
        r'^investment-support-directory/$',
        QuerystringRedirectView.as_view(url='/international/investment-support-directory/'),
        name='international-investment-support-directory-home',
    ),
    re_path(
        r'^investment-support-directory/(?P<path>[\w\-/]*)/$',
        QuerystringRedirectView.as_view(
            url=build_great_international_url('investment-support-directory/%(path)s/'),
            # Note that this then has a FURTHER redirect within great-international-ui
        ),
        name='international-investment-support-directory',
    ),
    re_path(
        r'^story/york-bag-retailer-goes-global-via-e-commerce/$',
        QuerystringRedirectView.as_view(url='/success-stories/york-bag-retailer-goes-global/'),
    ),
    re_path(
        r'^story/hello-babys-rapid-online-growth/$',
        QuerystringRedirectView.as_view(url='/success-stories/hello-babys-rapid-online-growth/'),
    ),
]


redirects += tos_redirects + contact_redirects + privacy_redirects + international_redirects + articles_redirects
