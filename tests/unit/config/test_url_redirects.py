import http

import pytest
from django.test import override_settings
from django.urls import reverse

from config.url_redirects import (
    INTERNATIONAL_COUNTRY_REDIRECTS_MAPPING,
    INTERNATIONAL_LANGUAGE_REDIRECTS_MAPPING,
    TOS_AND_PRIVACY_REDIRECT_LANGUAGES,
)
from core.cms_slugs import (
    DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
    PRIVACY_POLICY_URL,
    TERMS_URL,
)
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
    assert response.url == '/privacy/'


# the first element needs to end with a slash
redirects = [
    ('/about/', 'https://www.gov.uk/government/organisations/department-for-international-trade/about-our-services'),
    ('/jpm/', 'https://www.events.great.gov.uk/ehome/200197163/'),
    ('/brexit/', '/transition/'),
    ('/transition/', '/international/content/invest/how-to-setup-in-the-uk/transition-period/'),
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
    ('/uk/privacy-policy/', '/privacy/'),
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
        '/legacy/contact/feedback/selling_online_overseas/',
        '/contact/feedback/',
    ),
    (
        '/legacy/contact/feedback/single_sign_on/',
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
        '/legacy/contact/single_sign_on/',
        '/contact/triage/great-account/',
    ),
    (
        '/legacy/contact/single_sign_on/FeedbackForm/',
        '/contact/feedback/',
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
    (
        '/contact/triage/location/',
        DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
    ),
    (
        '/contact/triage/domestic/',
        DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
    ),
    # (
    #     '/contact/export-advice/comment/',
    #     '/contact/domestic/export-support/',
    # ),
    # (
    #     '/contact/export-advice/personal/',
    #     '/contact/domestic/export-support/',
    # ),
    # (
    #     '/contact/export-advice/business/',
    #     '/contact/domestic/export-support/',
    # ),
    # (
    #     '/contact/domestic/success/',
    #     '/contact/domestic/export-support/',
    # ),
    # (
    #     '/contact/office-finder/',
    #     DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
    # ),
    # CMS-1410 redirects for updated 'export advice' articles
    (
        '/advice/find-an-export-market/plan-export-market-research/',
        '/advice/find-an-export-market/understand-export-market-research/',
    ),
    (
        '/advice/find-an-export-market/define-export-market-potential/',
        '/learn/categories/market-research/market-research-approaches/online-research/',
    ),
    (
        '/advice/find-an-export-market/field-research-in-export-markets/',
        '/learn/categories/market-research/market-research-approaches/market-research/',
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
    ('/companion/', 'https://digital-companion.ava-digi.de/'),
]


@override_settings(FEATURE_FLAG_INTERNATIONAL_CONTACT_TRIAGE_ENABLED=True)
@pytest.mark.parametrize('url,expected', redirects)
def test_redirects(url, expected, client, settings):
    reload_urlconf_redirects()
    reload_urlconf()

    response = client.get(url)

    assert response.status_code == http.client.MOVED_PERMANENTLY or http.client.FOUND
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
        ('/market-research/visit-a-trade-show/', '/learn/categories/prepare-sell-new-country/'),
        ('/advice/find-an-export-market/trade-shows/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/market-research/doing-business-with-integrity/',
            'advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/',  # NOQA
        ),
        (
            '/market-research/know-the-relevant-legislation/',
            'advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/',  # NOQA
        ),
        ('/business-planning/', '/learn/categories/prepare-sell-new-country/'),
        ('/advice/define-route-to-market/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/business-planning/make-an-export-plan/',
            '/learn/categories/market-research/evaluate-opportunities/how-to-create-an-export-plan/',
        ),
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
            '/learn/categories/prepare-sell-new-country/routes-to-market/how-set-business-abroad/',
        ),
        ('/finance/', 'https://www.ukexportfinance.gov.uk/'),
        ('/advice/get-export-finance-and-funding/', 'https://www.ukexportfinance.gov.uk/'),
        (
            '/finance/choose-the-right-finance/',
            '/advice/get-export-finance-and-funding/choose-the-right-finance/',  # NOQA
        ),
        ('/finance/get-money-to-export/', '/advice/get-export-finance-and-funding/choose-the-right-finance/'),  # NOQA
        ('/finance/get-export-finance/', '/advice/get-export-finance-and-funding/get-export-finance/'),
        ('/finance/get-finance-support-from-government/', '/advice/get-export-finance-and-funding/get-export-finance/'),
        (
            '/advice/define-route-to-market/set-up-a-business-abroad/',
            '/learn/categories/prepare-sell-new-country/routes-to-market/how-set-business-abroad/',
        ),
        (
            '/finance/raise-money-by-borrowing/',
            '/advice/get-export-finance-and-funding/raise-money-by-borrowing/',  # NOQA
        ),
        ('/finance/borrow-against-assets/', '/advice/get-export-finance-and-funding/borrow-against-assets/'),
        (
            '/finance/raise-money-with-investment/',
            '/advice/get-export-finance-and-funding/raise-money-with-investment/',  # NOQA
        ),
        ('/getting-paid/', '/learn/categories/funding-financing-and-getting-paid/'),
        (
            '/advice/manage-payment-for-export-orders/payment-methods-for-exporters/',  # NOQA
            '/learn/categories/funding-financing-and-getting-paid/get-paid/payment-methods-exporters/',
        ),
        ('/advice/manage-payment-for-export-orders/', '/learn/categories/funding-financing-and-getting-paid/'),
        (
            '/getting-paid/invoice-currency-and-contents/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/payment-methods-exporters/',  # NOQA
        ),
        (
            '/getting-paid/invoice-currency-and-contents/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/payment-methods-exporters/',  # NOQA
        ),
        (
            '/getting-paid/consider-how-to-get-paid/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/how-create-export-invoice/',
        ),
        (
            '/advice/manage-payment-for-export-orders/how-to-create-an-export-invoice/',  # NOQA
            '/learn/categories/funding-financing-and-getting-paid/get-paid/how-create-export-invoice/',
        ),
        (
            '/advice/manage-payment-for-export-orders/decide-when-to-get-paid-for-export-orders/',  # NOQA
            '/learn/categories/funding-financing-and-getting-paid/get-paid/decide-when-get-paid-export-orders/',
        ),
        (
            '/getting-paid/decide-when-to-get-paid/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/decide-when-get-paid-export-orders/',  # NOQA
        ),
        (
            '/getting-paid/payment-methods/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/payment-methods-exporters/',  # NOQA
        ),
        (
            '/getting-paid/insure-against-non-payment/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/insure-against-non-payment/',  # NOQA
        ),
        (
            '/advice/manage-payment-for-export-orders/insure-against-non-payment/',  # NOQA
            '/learn/categories/funding-financing-and-getting-paid/get-paid/insure-against-non-payment/',
        ),
        ('/customer-insight/', '/learn/categories/prepare-sell-new-country/'),
        ('/advice/prepare-to-do-business-in-a-foreign-country/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/customer-insight/meet-your-customers/',
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-the-business-culture-in-the-market/',  # NOQA
        ),
        (
            '/customer-insight/know-your-customers/',
            '/advice/manage-legal-and-ethical-compliance/understand-business-risk-in-overseas-markets/',  # NOQA
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
        ('/new/next-steps/', '/advice/'),
        ('/occasional/next-steps/', '/advice/'),
        ('/regular/next-steps/', '/advice/'),
        ('/new/', '/advice/'),
        ('/occasional/', '/advice/'),
        ('/regular/', '/advice/'),
        (
            '/today/',
            '/international/content/capital-invest/',
        ),
        (
            '/trade/',
            '/international/trade/',
        ),
        (
            '/trade/some-term/',
            '/international/trade/incoming/some-term/',
        ),
        (
            '/trade/some-term/with/subpath/',
            '/international/trade/incoming/some-term/with/subpath/',
        ),
        (
            '/investment-support-directory/',
            '/international/investment-support-directory/',
        ),
        (
            '/investment-support-directory/some-term/',
            '/international/investment-support-directory/some-term/',
        ),
        (
            '/investment-support-directory/some-term/with/sub/path/',
            '/international/investment-support-directory/some-term/with/sub/path/',
        ),
        (
            '/story/york-bag-retailer-goes-global-via-e-commerce/',
            '/success-stories/york-bag-retailer-goes-global/',
        ),
        (
            '/story/hello-babys-rapid-online-growth/',
            '/success-stories/hello-babys-rapid-online-growth/',
        ),
        ('/advice/', '/learn/categories/'),
        ('/advice/create-an-export-plan/', '/learn/categories/market-research/'),
        ('/advice/find-an-export-market/trade-shows/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-understand-risks/',
            '/learn/categories/prepare-sell-new-country/managing-safety-corruption-and-business-integrity-risk/protect-your-business-bribery-and-corruption/',  # noqa:E501
        ),
        ('/advice/define-route-to-market/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/advice/create-an-export-plan/how-to-create-an-export-plan/',
            '/learn/categories/market-research/evaluate-opportunities/how-to-create-an-export-plan/',
        ),
        (
            '/advice/define-route-to-market/set-up-a-business-abroad/',
            '/learn/categories/prepare-sell-new-country/routes-to-market/how-set-business-abroad/',
        ),
        ('/advice/get-export-finance-and-funding/', 'https://www.ukexportfinance.gov.uk/'),
        (
            '/advice/manage-payment-for-export-orders/payment-methods-for-exporters/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/payment-methods-exporters/',
        ),
        (
            '/advice/manage-payment-for-export-orders/how-to-create-an-export-invoice/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/how-create-export-invoice/',
        ),
        (
            '/advice/manage-payment-for-export-orders/decide-when-to-get-paid-for-export-orders/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/decide-when-get-paid-export-orders/',
        ),
        (
            '/advice/manage-payment-for-export-orders/insure-against-non-payment/',
            '/learn/categories/funding-financing-and-getting-paid/get-paid/insure-against-non-payment/',
        ),
        ('/advice/manage-payment-for-export-orders/', '/learn/categories/funding-financing-and-getting-paid/'),
        ('/advice/prepare-to-do-business-in-a-foreign-country/', '/learn/categories/prepare-sell-new-country/'),
        ('/advice/find-an-export-market/', '/learn/categories/market-research/'),
        (
            '/advice/find-an-export-market/research-export-markets-online/',
            '/learn/categories/market-research/market-research-approaches/online-research/',
        ),
        ('/advice/find-an-export-market/understand-export-market-research/', '/learn/categories/market-research/'),
        (
            '/advice/find-an-export-market/research-in-market/',
            '/learn/categories/market-research/market-research-approaches/market-research/',
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/moving-goods-and-using-freight-forwarders/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/logistics-and-freight-forwarders/freight-forwarders/',  # noqa:E501
        ),
        (
            '/advice/use-incoterms-in-contracts/',
            '/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/',
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/international-trade-contracts-and-incoterms/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/logistics-and-freight-forwarders/incoterms/',  # noqa:E501
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/documentation-international-trade/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/get-your-goods-into-the-destination-country/understand-documentation-for-international-trade/',  # noqa:E501
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/get-your-export-documents-right/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/get-your-goods-into-the-destination-country/understand-documentation-for-international-trade/',  # noqa:E501
        ),
        ('/advice/define-route-to-market/understand-routes-to-market/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/advice/define-route-to-market/direct-sales/',
            '/learn/categories/prepare-sell-new-country/routes-to-market/sell-direct-your-customer/',
        ),
        (
            '/advice/define-route-to-market/use-an-agent-or-distributor/',
            '/learn/categories/prepare-sell-new-country/routes-to-market/when-use-agent-or-distributor/',
        ),
        ('/advice/define-route-to-market/use-licensing-or-franchising/', '/learn/categories/prepare-sell-new-country/'),
        (
            '/advice/define-route-to-market/establish-a-joint-venture-agreement/',
            '/learn/categories/prepare-sell-new-country/routes-to-market/set-joint-ventures-abroad/',
        ),
        (
            '/advice/prepare-to-do-business-in-a-foreign-country/visiting-market/',
            '/learn/categories/prepare-sell-new-country/',
        ),
        (
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-local-business-culture/',
            '/learn/categories/prepare-sell-new-country/different-ways-of-doing-business-across-borders/understand-local-business-culture-your-target-market/',  # noqa:E501
        ),
        (
            '/advice/prepare-to-do-business-in-a-foreign-country/understand-business-risks-when-exporting/',
            '/learn/categories/prepare-sell-new-country/',
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/',
        ),
        (
            '/advice/manage-risk-bribery-corruption-and-abuse-human-rights/',
            '/learn/categories/prepare-sell-new-country/',
        ),
        (
            '/advice/manage-risk-bribery-corruption-and-abuse-human-rights/bribery-and-corruption-manage-risks/',
            '/learn/categories/prepare-sell-new-country/managing-safety-corruption-and-business-integrity-risk/protect-your-business-bribery-and-corruption/',  # noqa:E501
        ),
        (
            '/advice/manage-risk-bribery-corruption-and-abuse-human-rights/human-rights-violations-recognise-and-manage-risks/',  # noqa:E501
            '/learn/categories/prepare-sell-new-country/managing-safety-corruption-and-business-integrity-risk/operating-business-integrity/',  # noqa:E501
        ),
        (
            '/advice/prepare-for-export-procedures-and-logistics/understand-international-trade-terms/',
            '/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/get-your-goods-into-the-destination-country/understand-international-trade-terms/',  # noqa:E501
        ),
        ('/advice/sell-services-overseas/', '/learn/categories/prepare-sell-new-country/selling-services-overseas/'),
        (
            '/advice/sell-services-overseas/deliver-services-overseas/',
            '/learn/categories/prepare-sell-new-country/selling-services-overseas/how-to-deliver-services-overseas/',
        ),
        (
            '/advice/sell-services-overseas/market-your-services-overseas/',
            '/learn/categories/prepare-sell-new-country/selling-services-overseas/how-to-market-your-services-overseas/',  # noqa:E501
        ),
        (
            '/advice/sell-services-overseas/prepare-to-sell-services-overseas/',
            '/learn/categories/prepare-sell-new-country/selling-services-overseas/prepare-to-sell-services-overseas/',
        ),
    ],
)
def test_redirect_articles(incoming_url, expected_url, client):
    response = client.get(incoming_url)
    assert response.status_code == http.client.MOVED_PERMANENTLY or http.client.FOUND
    assert response.url == expected_url
