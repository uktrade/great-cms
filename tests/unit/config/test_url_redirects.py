import http

import pytest
from django.test import override_settings
from django.urls import reverse

from config.url_redirects import (
    INTERNATIONAL_COUNTRY_REDIRECTS_MAPPING,
    INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING,
    TOS_AND_PRIVACY_REDIRECT_LANGUAGES,
)
from core.cms_slugs import PRIVACY_POLICY_URL, TERMS_URL
from core.tests.helpers import reload_urlconf, reload_urlconf_redirects

pytestmark = pytest.mark.django_db

UTM_QUERY_PARAMS = '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'


def add_utm_query_params(url):
    return '{url}{utm_query_params}'.format(url=url, utm_query_params=UTM_QUERY_PARAMS)


def get_redirect_mapping_param_values(redirect_mapping, url_patterns):
    param_values = []
    for path, expected in redirect_mapping:
        for url_pattern in url_patterns:
            param_values.append((url_pattern.format(path=path), expected))

    return param_values


# Generate a list of URLs for all paths (e.g. /de and /int/de) with and without
# trailing slash
language_redirects = get_redirect_mapping_param_values(
    redirect_mapping=INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING,
    url_patterns=(
        '/int/{path}/',
        '/int/{path}',
        # SJ: I'm _assuming_ the /int prefix above is legacy from some previous path convention...
        '/{path}/',
        '/{path}',
    ),
)
country_redirects = get_redirect_mapping_param_values(
    redirect_mapping=INTERNATIONAL_COUNTRY_REDIRECTS_MAPPING, url_patterns=('/{path}/', '/{path}')
)
INTERNATIONAL_REDIRECTS_PARAMS = ('url,expected_language', language_redirects + country_redirects)


@pytest.mark.parametrize(*INTERNATIONAL_REDIRECTS_PARAMS)
def test_international_redirects_no_query_params(url, expected_language, client):

    if not url.endswith('/'):
        url = client.get(url).url

    response = client.get(url, follow=False)

    assert response.status_code == http.client.FOUND
    assert response.url == '/international/?lang={expected_language}'.format(expected_language=expected_language)


@pytest.mark.parametrize(*INTERNATIONAL_REDIRECTS_PARAMS)
def test_international_redirects_query_params(url, expected_language, client):

    if not url.endswith('/'):
        url = client.get(add_utm_query_params(url)).url
    else:
        url = add_utm_query_params(url)

    response = client.get(url, follow=False)

    assert response.status_code == http.client.FOUND
    assert response.url == (
        '/international/{utm_query_params}&lang={expected_language}'.format(
            utm_query_params=UTM_QUERY_PARAMS, expected_language=expected_language
        )
    )


@pytest.mark.parametrize('path', TOS_AND_PRIVACY_REDIRECT_LANGUAGES)
def test_tos_international_redirect(path, client):
    response = client.get('/int/{path}/terms-and-conditions/'.format(path=path))

    assert response.status_code == http.client.FOUND
    assert response.url == TERMS_URL


@pytest.mark.parametrize('path', TOS_AND_PRIVACY_REDIRECT_LANGUAGES)
def test_privacy_international_redirect(path, client):
    response = client.get('/int/{path}/privacy-policy/'.format(path=path))

    assert response.status_code == http.client.FOUND
    assert response.url == '/privacy-and-cookies/'


# the first element needs to end with a slash
redirects = [
    ('/about/', 'https://www.gov.uk/government/organisations/department-for-international-trade/about-our-services'),
    ('/jpm/', 'https://www.events.great.gov.uk/ehome/200197163/'),
    ('/brexit/', '/transition/'),
    ('/transition/', '/international/content/invest/how-to-setup-in-the-uk/transition-period/'),
    ('/eu-exit-news/contact/', '/transition-period/contact/'),
    ('/eu-exit-news/contact/success/', '/transition-period/contact/success/'),
    ('/redarrows/', 'https://www.events.great.gov.uk/red-arrows-north-america-tour/'),
    (
        '/new-zealand-event-calendar/',
        'https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=zealand',
    ),
    ('/story/online-marketplaces-propel-freestyle-xtreme-sales/', '/'),
    (
        '/australia-event-calendar/',
        'https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events?keyword=australia',
    ),
    ('/trskorea/', 'https://eu.eventscloud.com/korea-uk-tech-rocketship-awards-kr'),
    ('/TRSkorea/', 'https://eu.eventscloud.com/korea-uk-tech-rocketship-awards-kr'),
    ('/ukti/', '/'),
    ('/UKTI/', '/'),
    ('/future/', 'https://www.events.great.gov.uk/ehome/index.php?eventid=200185206'),
    ('/innovation-hk/', 'https://www.events.great.gov.uk/ehome/innovation-hk'),
    ('/innovation-china/', 'https://www.events.great.gov.uk/ehome/innovation-china'),
    ('/innovation-asean/', 'https://www.events.great.gov.uk/ehome/innovation-asean'),
    ('/innovation-au-nz/', 'https://www.events.great.gov.uk/ehome/innovation-au-nz'),
    ('/innovation-jpn/', 'https://www.events.great.gov.uk/ehome/innovation-jpn'),
    ('/innovation-kor/', 'https://www.events.great.gov.uk/ehome/innovation-kor'),
    ('/bodw2019/', 'https://www.events.great.gov.uk/bodw2019/'),
    ('/events/', 'https://www.events.great.gov.uk/'),
    ('/ukpavilion2020/', 'https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ('/beijingexpo2019/', 'https://www.events.great.gov.uk/ehome/index.php?eventid=200188985&'),
    ('/expo2020/', 'https://www.events.trade.gov.uk/dubai-expo-2020/'),
    ('/invest/', '/international/invest'),
    ('/int/invest/', '/international/invest'),
    ('/us/invest/', '/international/invest'),
    ('/cn/invest/', '/international/invest?lang=zh-hans'),
    ('/de/invest/', '/international/invest?lang=de'),
    ('/in/invest/', '/international/invest'),
    ('/es/invest/', '/international/invest?lang=es'),
    ('/int/es/invest/', '/international/invest?lang=es'),
    ('/int/zh/invest/', '/international/invest?lang=zh-hans'),
    ('/int/pt/invest/', '/international/invest?lang=pt'),
    ('/br/invest/', '/international/invest'),
    ('/int/de/invest/', '/international/invest?lang=de'),
    ('/jp/invest/', '/international/invest?lang=ja'),
    ('/int/ja/invest/', '/international/invest?lang=ja'),
    ('/int/ar/invest/', '/international/invest'),
    ('/study/', 'https://study-uk.britishcouncil.org'),
    ('/visit/', 'https://www.visitbritain.com/gb/en'),
    ('/export/', '/'),
    ('/export/new/', '/advice/'),
    ('/export/occasional/', '/advice/'),
    ('/export/regular/', '/advice/'),
    ('/export/opportunities/', '/export-opportunities/'),
    ('/opportunities/', '/export-opportunities/'),
    (
        (
            '/opportunities/usa-'
            'centre-for-medicare-and-medicaid-services-hospital-improvement'
            '-innovation-network-hiin-rfp/'
        ),
        (
            '/export-opportunities/usa-'
            'centre-for-medicare-and-medicaid-services-hospital-improvement'
            '-innovation-network-hiin-rfp/'
        ),
    ),
    (
        (
            '/opportunities/usa-'
            'centre-for-medicare-and-medicaid-services-hospital-improvement'
            '-innovation-network-hiin-rfp/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
        (
            '/export-opportunities/usa-'
            'centre-for-medicare-and-medicaid-services-hospital-improvement'
            '-innovation-network-hiin-rfp/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
    ),
    (
        ('/opportunities/' 'mexico-craft-beer-distributor-looking-for-international-brands/'),
        ('/export-opportunities/' 'mexico-craft-beer-distributor-looking-for-international-brands/'),
    ),
    (
        (
            '/opportunities/'
            'mexico-craft-beer-distributor-looking-for-international-brands/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
        (
            '/export-opportunities/'
            'mexico-craft-beer-distributor-looking-for-international-brands/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
    ),
    (
        ('/opportunities/' 'taiwan-2018-flora-expo-seeking' '-suppliers-to-help-develop-exhibition/'),
        ('/export-opportunities/' 'taiwan-2018-flora-expo-seeking' '-suppliers-to-help-develop-exhibition/'),
    ),
    (
        (
            '/opportunities/'
            'taiwan-2018-flora-expo-seeking'
            '-suppliers-to-help-develop-exhibition/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
        (
            '/export-opportunities/'
            'taiwan-2018-flora-expo-seeking'
            '-suppliers-to-help-develop-exhibition/'
            '?utm_source=test%12&utm_medium=test&utm_campaign=test%test'
        ),
    ),
    ('/export/find-a-buyer/', '/find-a-buyer/'),
    ('/export/selling-online-overseas/', '/selling-online-overseas/'),
    ('/uk/privacy-policy/', '/privacy-and-cookies/'),
    ('/uk/terms-and-conditions/', '/terms-and-conditions/'),
    ('/int/', '/international/'),
    ('/uk/', '/'),
    ('/in/', '/international/'),
    ('/us/', '/international/'),
    ('/innovation/', ('https://www.events.trade.gov.uk/' 'the-great-festival-of-innovation-hong-kong-2018/')),
    ('/uk/cy/', ('https://www.great.gov.uk/?utm_source=Mailing&utm_medium' '=Brochure&utm_campaign=ExportBrochureCY')),
    ('/verify/', '/find-a-buyer/verify/letter-confirm/'),
    (
        '/kr/',
        (
            'https://www.events.trade.gov.uk/invest-in-great---korea'
            '?utm_source=print&utm_campaign=korean_winter_olympics_invest'
        ),
    ),
    (
        '/legacy/contact/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/contact/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/directory/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/directory/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/eig/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/export-opportunities/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/export_opportunities/',
        '/contact/triage/domestic/',
    ),
    (
        '/legacy/contact/export_opportunities/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/export_ops/',
        '/contact/triage/domestic/',
    ),
    (
        '/legacy/contact/export_readiness/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/datahub/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/directory/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/e_navigator/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/eig/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/export_ops/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/exportingisgreat/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/exportopportunities/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/invest/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/opportunities/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/selling-online-overseas/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/selling_online_overseas/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/single_sign_on/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/soo/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/sso/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/invest/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/opportunities/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/selling_online_overseas/',
        '/contact/triage/domestic/',
    ),
    (
        '/legacy/contact/selling_online_overseas/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/single_sign_on/',
        '/contact/triage/great-account/',
    ),
    (
        '/legacy/contact/single_sign_on/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/soo/feedback/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/soo/FeedbackForm/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/soo/Triage/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/soo/TriageForm/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/triage/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/triage/directory/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/triage/soo/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/triage/sso/',
        '/contact/triage/location/',
    ),
    (
        '/legacy/contact/cookies/',
        PRIVACY_POLICY_URL,
    ),
    (
        '/legacy/contact/terms-and-conditions/',
        TERMS_URL,
    ),
    # CMS-1410 redirects for updated 'export advice' articles
    (
        '/advice/find-an-export-market/plan-export-market-research/',
        '/advice/find-an-export-market/understand-export-market-research/',
    ),
    (
        '/advice/find-an-export-market/define-export-market-potential/',
        '/advice/find-an-export-market/research-export-markets-online/',
    ),
    (
        '/advice/find-an-export-market/field-research-in-export-markets/',
        '/advice/find-an-export-market/research-in-market/',
    ),
    (
        '/advice/get-export-finance-and-funding/choose-the-right-finance/',
        '/advice/get-export-finance-and-funding/understand-export-finance/',
    ),
    (
        '/advice/get-export-finance-and-funding/raise-money-by-borrowing/',
        '/advice/get-export-finance-and-funding/get-export-finance/',
    ),
    (
        '/advice/get-export-finance-and-funding/borrow-against-assets/',
        '/advice/get-export-finance-and-funding/get-export-finance/',
    ),
    (
        '/advice/get-export-finance-and-funding/raise-money-with-investment/',  # NOQA
        '/advice/get-export-finance-and-funding/get-export-finance/',
    ),
    (
        '/contact/triage/international/',
        '/international/contact/',
    ),
]


@override_settings(FEATURE_FLAG_INTERNATIONAL_CONTACT_TRIAGE_ENABLED=True)
@pytest.mark.parametrize('url,expected', redirects)
def test_redirects(url, expected, client, settings):
    reload_urlconf_redirects()
    reload_urlconf()

    response = client.get(url)

    assert response.status_code == http.client.FOUND
    if not expected.startswith('http') and not expected.startswith('/'):
        expected = reverse(expected)

    assert response.url == expected


# add urls with no trailing slash
redirects_no_slash = [(redirect[0].split('?')[0][:-1], redirect[1]) for redirect in redirects]


@pytest.mark.parametrize('url,expected', redirects_no_slash)
def test_redirects_no_trailing_slash(url, expected, client):
    response = client.get(url)
    assert response.status_code == http.client.MOVED_PERMANENTLY, url


@pytest.mark.parametrize(
    'incoming_url,expected_url',
    [
        ('/market-research/', '/advice/find-an-export-market/'),
        ('/market-research/do-research-first/', '/advice/find-an-export-market/plan-export-market-research/'),
        ('/market-research/define-market-potential/', '/advice/find-an-export-market/define-export-market-potential/'),
        ('/market-research/analyse-the-competition/', '/advice/find-an-export-market/define-export-market-potential/'),
        (
            '/market-research/research-your-market/',
            '/advice/find-an-export-market/field-research-in-export-markets/',  # NOQA
        ),
        ('/market-research/visit-a-trade-show/', '/advice/find-an-export-market/trade-shows/'),
        (
            '/market-research/doing-business-with-integrity/',
            '/advice/manage-legal-and-ethical-compliance/understand-business-risks-in-overseas-markets/',  # NOQA
        ),
        (
            '/market-research/know-the-relevant-legislation/',
            '/advice/manage-legal-and-ethical-compliance/understand-business-risks-in-overseas-markets/',  # NOQA
        ),
        ('/business-planning/', '/advice/define-route-to-market/'),
        ('/business-planning/make-an-export-plan/', '/advice/create-an-export-plan/how-to-create-an-export-plan/'),
        ('/business-planning/find-a-route-to-market/', '/advice/define-route-to-market/routes-to-market/'),
        ('/business-planning/sell-overseas-directly/', '/advice/define-route-to-market/sell-overseas-directly/'),
        ('/business-planning/use-an-overseas-agent/', '/advice/define-route-to-market/export-agents/'),
        ('/business-planning/choosing-an-agent-or-distributor/', '/advice/define-route-to-market/export-agents/'),
        ('/business-planning/use-a-distributor/', '/advice/define-route-to-market/export-distributors/'),
        (
            '/business-planning/license-your-product-or-service/',
            '/advice/define-route-to-market/create-a-licensing-agreement/',
        ),
        (
            '/business-planning/licensing-and-franchising/',
            '/advice/define-route-to-market/create-a-licensing-agreement/',
        ),
        ('/business-planning/franchise-your-business/', '/advice/define-route-to-market/create-a-franchise-agreement/'),
        (
            '/business-planning/start-a-joint-venture/',
            '/advice/define-route-to-market/create-a-joint-venture-agreement/',  # NOQA
        ),
        (
            '/business-planning/set-up-an-overseas-operation/',
            '/advice/define-route-to-market/set-up-a-business-abroad/',
        ),
        ('/finance/', '/advice/get-export-finance-and-funding/'),
        (
            '/finance/choose-the-right-finance/',
            '/advice/get-export-finance-and-funding/choose-the-right-finance/',  # NOQA
        ),
        ('/finance/get-money-to-export/', '/advice/get-export-finance-and-funding/choose-the-right-finance/'),  # NOQA
        ('/finance/get-export-finance/', '/advice/get-export-finance-and-funding/get-export-finance/'),
        ('/finance/get-finance-support-from-government/', '/advice/get-export-finance-and-funding/get-export-finance/'),
        (
            '/finance/raise-money-by-borrowing/',
            '/advice/get-export-finance-and-funding/raise-money-by-borrowing/',  # NOQA
        ),
        ('/finance/borrow-against-assets/', '/advice/get-export-finance-and-funding/borrow-against-assets/'),
        (
            '/finance/raise-money-with-investment/',
            '/advice/get-export-finance-and-funding/raise-money-with-investment/',  # NOQA
        ),
        ('/getting-paid/', '/advice/manage-payment-for-export-orders/'),
        (
            '/getting-paid/invoice-currency-and-contents/',
            '/advice/manage-payment-for-export-orders/payment-methods-for-exporters/',  # NOQA
        ),
        (
            '/getting-paid/consider-how-youll-get-paid/',
            '/advice/manage-payment-for-export-orders/how-to-create-an-export-invoice/',  # NOQA
        ),
        (
            '/getting-paid/decide-when-youll-get-paid/',
            '/advice/manage-payment-for-export-orders/decide-when-youll-get-paid-for-export-orders/',  # NOQA
        ),
        (
            '/getting-paid/payment-methods/',
            '/advice/manage-payment-for-export-orders/payment-methods-for-exporters/',  # NOQA
        ),
        (
            '/getting-paid/insure-against-non-payment/',
            '/advice/manage-payment-for-export-orders/insure-against-non-payment/',  # NOQA
        ),
        ('/customer-insight/', '/advice/prepare-to-do-business-in-a-foreign-country/'),
        (
            '/customer-insight/meet-your-customers/',
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/',  # NOQA
        ),
        (
            '/customer-insight/know-your-customers/',
            '/advice/manage-legal-and-ethical-compliance/understand-business-risks-in-overseas-markets/',  # NOQA
        ),
        (
            '/customer-insight/manage-language-differences/',
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/',  # NOQA
        ),
        (
            '/customer-insight/understand-your-customers-culture/',
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/',  # NOQA
        ),
        ('/operations-and-compliance/', '/advice/manage-legal-and-ethical-compliance/'),
        (
            '/operations-and-compliance/internationalise-your-website/',
            '/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/',  # NOQA
        ),
        (
            '/operations-and-compliance/match-your-website-to-your-audience/',  # NOQA
            '/advice/prepare-to-do-business-in-a-foreign-country/internationalise-your-website/',  # NOQA
        ),
        (
            '/operations-and-compliance/protect-your-intellectual-property/',  # NOQA
            '/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/',  # NOQA
        ),
        (
            '/operations-and-compliance/types-of-intellectual-property/',
            '/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/',  # NOQA
        ),
        (
            '/operations-and-compliance/know-what-ip-you-have/',
            '/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/',  # NOQA
        ),
        (
            '/operations-and-compliance/international-ip-protection/',
            '/advice/manage-legal-and-ethical-compliance/protect-your-intellectual-property-when-exporting/',  # NOQA
        ),
        (
            '/operations-and-compliance/report-corruption/',
            '/advice/manage-legal-and-ethical-compliance/report-corruption-and-human-rights-violations/',  # NOQA
        ),
        (
            '/operations-and-compliance/anti-bribery-and-corruption-training/',  # NOQA
            '/advice/manage-legal-and-ethical-compliance/anti-bribery-and-corruption-training/',  # NOQA
        ),
        (
            '/operations-and-compliance/plan-the-logistics/',
            '/advice/prepare-for-export-procedures-and-logistics/plan-logistics-for-exporting/',  # NOQA
        ),
        (
            '/operations-and-compliance/get-your-export-documents-right/',
            '/advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/',  # NOQA
        ),
        (
            '/operations-and-compliance/use-a-freight-forwarder/',
            '/advice/prepare-for-export-procedures-and-logistics/use-a-freight-forwarder-to-export/',  # NOQA
        ),
        (
            '/operations-and-compliance/use-incoterms-in-contracts/',
            '/advice/prepare-for-export-procedures-and-logistics/use-incoterms-in-contracts/',  # NOQA
        ),
        ('/new/next-steps/', '/advice'),
        ('/occasional/next-steps/', '/advice'),
        ('/regular/next-steps/', '/advice'),
        ('/new/', '/advice'),
        ('/occasional/', '/advice'),
        ('/regular/', '/advice'),
        (
            '/brexit/contact/',
            '/transition-period/contact/',
        ),
        (
            '/brexit/contact/success/',
            '/transition-period/contact/success/',
        ),
        (
            '/today/',
            '/international/content/capital-invest/',
        ),
        ('/trade/some-term/', '/international/trade/incoming/some-term/'),
        ('/investment-support-directory/some-term/', '/international/investment-support-directory/some-term/'),
    ],
)
def redirect_articles(incoming_url, expected_url, client):
    response = client.get(incoming_url)
    assert response.status_code == 302
    assert response.url == expected_url
