from datetime import datetime

from django.conf import settings
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import get_language_bidi, gettext as _

from core import cms_slugs
from core.helpers import international_url
from directory_constants import choices, urls
from domestic_growth.constants import EXISTING_TRIAGE_URL, PRE_START_TRIAGE_URL


def javascript_components(request):
    password_reset_url = urls.domestic.SINGLE_SIGN_ON / 'accounts/password/reset/'
    data = {
        'linkedin_url': settings.SSO_OAUTH2_LINKEDIN_URL,
        'google_url': settings.SSO_OAUTH2_GOOGLE_URL,
        'terms_url': urls.domestic.TERMS_AND_CONDITIONS,
        'password_reset_url': password_reset_url,
        'industry_options': [{'value': key, 'label': label} for key, label in choices.SECTORS],
        'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
    }
    return {'javascript_components': data}


def env_vars(request):
    data = dict()
    data['great_support_email'] = settings.GREAT_SUPPORT_EMAIL
    data['dit_on_govuk'] = settings.DIT_ON_GOVUK
    data['cia_factbook_url'] = settings.CIA_FACTBOOK_URL
    data['check_duties_url'] = settings.CHECK_DUTIES_URL
    data['world_bank_url'] = settings.WORLD_BANK_URL
    data['data_world_bank_url'] = settings.DATA_WORLD_BANK_URL
    data['united_nations_url'] = settings.UNITED_NATIONS_URL
    data['base_url'] = settings.BASE_URL
    return data


def analytics_vars(request):
    return {
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
        'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
        'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
    }


def sentry_vars(request):
    return {
        'APP_ENVIRONMENT': settings.APP_ENVIRONMENT,
        'SENTRY_DSN': settings.SENTRY_DSN,
        'SENTRY_BROWSER_TRACES_SAMPLE_RATE': settings.SENTRY_BROWSER_TRACES_SAMPLE_RATE,
    }


def cookie_management_vars(request):
    return {
        'PRIVACY_COOKIE_DOMAIN': settings.PRIVACY_COOKIE_DOMAIN,
    }


def cms_slug_urls(request):
    return {
        'DASHBOARD_URL': cms_slugs.DASHBOARD_URL,
        'LOGIN_URL': cms_slugs.LOGIN_URL,
        'PRIVACY_POLICY_URL': cms_slugs.PRIVACY_POLICY_URL,
    }


def migration_support_vars(request):
    # Context vars that help with the migration from Great V1 to V2
    return {
        'BREADCRUMBS_ROOT_URL': settings.BREADCRUMBS_ROOT_URL,
        'FEATURE_SHOW_REPORT_BARRIER_CONTENT': settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT,
        'FEATURE_SHOW_BRAND_BANNER': settings.FEATURE_SHOW_BRAND_BANNER,
    }


def feature_flags(request):
    """General way to make feature flags available in the template"""
    retval = {'features': {}}
    retval['features'].update(settings.SSO_PROFILE_FEATURE_FLAGS)
    retval['features']['FEATURE_PRODUCT_EXPERIMENT_LINKS'] = settings.FEATURE_PRODUCT_EXPERIMENT_LINKS
    retval['features']['FEATURE_DIGITAL_POINT_OF_ENTRY'] = settings.FEATURE_DIGITAL_POINT_OF_ENTRY
    retval['features']['FEATURE_DESIGN_SYSTEM'] = settings.FEATURE_DESIGN_SYSTEM
    retval['features']['FEATURE_COURSES_LANDING_PAGE'] = settings.FEATURE_COURSES_LANDING_PAGE
    retval['features']['FEATURE_DEA_V2'] = settings.FEATURE_DEA_V2
    retval['features']['FEATURE_SHOW_OLD_CONTACT_FORM'] = settings.FEATURE_SHOW_OLD_CONTACT_FORM
    retval['features']['FEATURE_HOMEPAGE_REDESIGN_V1'] = settings.FEATURE_HOMEPAGE_REDESIGN_V1
    retval['features']['FEATURE_SHARE_COMPONENT'] = settings.FEATURE_SHARE_COMPONENT
    retval['features']['FEATURE_PRODUCT_MARKET_HERO'] = settings.FEATURE_PRODUCT_MARKET_HERO
    retval['features']['FEATURE_PRODUCT_MARKET_SEARCH_ENABLED'] = settings.FEATURE_PRODUCT_MARKET_SEARCH_ENABLED
    retval['features']['FEATURE_SHOW_USA_CTA'] = settings.FEATURE_SHOW_USA_CTA
    retval['features']['FEATURE_SHOW_EU_CTA'] = settings.FEATURE_SHOW_EU_CTA
    retval['features'][
        'FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_CHINA'
    ] = settings.FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_CHINA
    retval['features'][
        'FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_GERMANY'
    ] = settings.FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_GERMANY
    retval['features'][
        'FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_USA'
    ] = settings.FEATURE_SHOW_MARKET_GUIDE_SECTOR_SPOTLIGHT_USA

    retval['features']['FEATURE_DESIGN_SYSTEM'] = settings.FEATURE_DESIGN_SYSTEM

    retval['features']['FEATURE_GREAT_ERROR'] = settings.FEATURE_GREAT_ERROR
    retval['features']['FEATURE_GUIDED_JOURNEY'] = settings.FEATURE_GUIDED_JOURNEY
    retval['features']['FEATURE_GUIDED_JOURNEY_EXTRAS'] = settings.FEATURE_GUIDED_JOURNEY_EXTRAS
    retval['features']['FEATURE_GUIDED_JOURNEY_ENHANCED_SEARCH'] = settings.FEATURE_GUIDED_JOURNEY_ENHANCED_SEARCH
    retval['features']['FEATURE_UNGUIDED_JOURNEY'] = settings.FEATURE_UNGUIDED_JOURNEY

    retval['features']['FEATURE_GREAT_MIGRATION_BANNER'] = settings.FEATURE_GREAT_MIGRATION_BANNER

    retval['features']['FEATURE_DOMESTIC_GROWTH'] = settings.FEATURE_DOMESTIC_GROWTH
    retval['features']['FEATURE_BGS_CHAT'] = settings.FEATURE_BGS_CHAT

    return retval


def directory_components_html_lang_attribute(request):
    return {'directory_components_html_lang_attribute': translation.get_language()}


def services_home_links(request):
    return {
        'international_home_link': {'url': reverse_lazy('index'), 'label': _('great.gov.uk international')},
    }


def domestic_header(request):
    search_icon = (
        '<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" class="great-ds-icon-svg" width="20" height="20" '
        'viewBox="0 0 18 18" fill="currentColor"><path fill-rule="evenodd" clip-rule="evenodd" '
        'd="M7.77589 13.722C6.26697 13.8589 4.79933 13.386 3.64011 12.4016C1.2472 10.3681 0.933108 6.74217 '
        '2.94069 4.31856C4.06024 2.96784 5.66793 2.27198 7.28695 2.27198C8.57164 2.27198 9.86443 2.7113 '
        '10.9249 3.61205C12.0841 4.59641 12.7949 5.97992 12.9268 7.50687C13.0588 9.03299 12.5957 10.5206 '
        '11.6235 11.6943C10.6505 12.868 9.28401 13.5884 7.77589 13.722ZM18 15.5071L13.5606 11.7361C14.3256 '
        '10.4247 14.6737 8.91169 14.5393 7.36344C14.3702 5.40128 13.4562 3.62271 11.9651 2.35558C8.88816 '
        '-0.258992 4.28286 0.148357 1.70133 3.26536C-0.881003 6.38072 -0.477867 11.0427 2.59908 13.6573C3.92344 '
        '14.7826 5.56107 15.3834 7.26914 15.3834C7.48447 15.3834 7.70061 15.3744 7.91756 15.3555C9.44591 '
        '15.2203 10.8569 14.6097 11.9999 13.6196L16.4385 17.3914L18 15.5071Z"/></svg>'
    )
    menu_icon = (
        '<svg aria-hidden="true" class="great-ds-icon-svg great-ds-icon--menu" width="16" height="17" '
        'viewBox="0 0 16 17" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" '
        'class="great-ds-icon--menu-bars"'
        'd="M1 3.5C1 2.94687 1.44687 2.5 2 2.5H14C14.5531 2.5 15 2.94687 15 3.5C15 4.05313 14.5531 4.5 14 '
        '4.5H2C1.44687 4.5 1 4.05313 1 3.5ZM1 8.5C1 7.94688 1.44687 7.5 2 7.5H14C14.5531 7.5 15 7.94688 15 '
        '8.5C15 9.05312 14.5531 9.5 14 9.5H2C1.44687 9.5 1 9.05312 1 8.5ZM15 13.5C15 14.0531 14.5531 14.5 14 '
        '14.5H2C1.44687 14.5 1 14.0531 1 13.5C1 12.9469 1.44687 12.5 2 12.5H14C14.5531 12.5 15 12.9469 15 '
        '13.5Z"/><path fill="currentColor" class="great-ds-icon--menu-close" d="M10.085 8.5L13.2122 5.37281C13.5959 '
        '4.98906 13.5959 4.36687 13.2122 3.98281L12.5172 3.28781C12.1334 2.90406 11.5113 2.90406 11.1272 '
        '3.28781L8 6.415L4.87281 3.28781C4.48906 2.90406 3.86688 2.90406 3.48281 3.28781L2.78781 3.98281C2.40406 '
        '4.36656 2.40406 4.98875 2.78781 5.37281L5.915 8.5L2.78781 11.6272C2.40406 12.0109 2.40406 12.6331 '
        '2.78781 13.0172L3.48281 13.7122C3.86656 14.0959 4.48906 14.0959 4.87281 13.7122L8 10.585L11.1272 '
        '13.7122C11.5109 14.0959 12.1334 14.0959 12.5172 13.7122L13.2122 13.0172C13.5959 12.6334 13.5959 '
        '12.0113 13.2122 11.6272L10.085 8.5Z"/></svg>'
    )

    return {
        'header_classes': '',
        'isInternational': False,
        'sso_is_logged_in': request.user.is_authenticated,
        'isAuthenticated': request.user.is_authenticated,
        'hideSearch': False,
        'hideMenuOnDesktop': False,
        'use_domestic_logo': True,
        'domesticLink': {'href': '/', 'text': 'Export from the UK'},
        'internationalLink': {'href': f'/{international_url(request)}/', 'text': 'Invest in the UK'},
        'searchFormAction': reverse_lazy('search:search'),
        'navItemsList': [
            {
                'href': '/learn/categories/',
                'text': 'Learn to export',
                'isCurrent': '/learn/categories/' in request.path,
            },
            {
                'href': reverse_lazy('core:compare-countries'),
                'text': 'Where to export',
                'requiresAuth': True,
                'isCurrent': '/compare-countries' in request.path,
            },
            {
                'href': '/export-plan/',
                'text': 'Make an export plan',
                'requiresAuth': True,
                'isCurrent': '/export-plan' in request.path,
            },
            {'href': '/markets/', 'text': 'Markets', 'requiresNoAuth': True, 'isCurrent': '/markets' in request.path},
            {
                'href': '/services/',
                'text': 'Services',
                'requiresNoAuth': True,
                'isCurrent': '/services' in request.path,
            },
        ],
        'menuItemsList': [
            {
                'text': f'Hi {request.user.first_name}' if request.user.is_authenticated else '',
                'userGreeting': True,
                'requiresAuth': True,
            },
            {
                'href': '/dashboard/',
                'text': 'Dashboard',
                'requiresAuth': True,
                'isCurrent': '/dashboard' in request.path,
            },
            {
                'href': reverse_lazy('core:compare-countries'),
                'text': 'Where to export',
                'requiresAuth': True,
                'isCurrent': '/compare-countries' in request.path,
            },
            {
                'href': '/export-plan/',
                'text': 'Make an export plan',
                'requiresAuth': True,
                'isCurrent': '/export-plan' in request.path,
            },
            {'href': '/profile/', 'text': 'Account', 'requiresAuth': True, 'isCurrent': '/profile' in request.path},
            {
                'href': '/learn/categories/',
                'text': 'Learn to export',
                'isCurrent': '/learn/categories/' in request.path,
            },
            {'href': '/markets/', 'text': 'Markets', 'isCurrent': '/markets' in request.path},
            {'href': '/services/', 'text': 'Services', 'isCurrent': '/services' in request.path},
            {'text': 'Sign out', 'attributes': 'onclick="signOut()"', 'button': True, 'requiresAuth': True},
            {'text': 'Sign in', 'href': reverse_lazy('core:login'), 'button': True, 'requiresNoAuth': True},
        ],
        'actionLinkList': [
            {'href': '/dashboard/', 'text': 'Dashboard', 'requiresAuth': True},
            {'href': reverse_lazy('core:login'), 'text': 'Sign in', 'requiresNoAuth': True},
        ],
        'mobileSiteLink': {'href': f'/{international_url(request)}', 'text': 'Invest in the UK'},
        'search_icon': search_icon,
        'menu_icon': menu_icon,
        'bgs_header_context': {
            'header_classes': '',
            'sso_is_logged_in': request.user.is_authenticated,
            'isAuthenticated': request.user.is_authenticated,
            'hideSearch': False,
            'hideMenuOnDesktop': False,
            'searchFormAction': reverse_lazy('search:search'),
            'search_icon': search_icon,
            'menu_icon': menu_icon,
            'menuItemsList': [
                {
                    'icon': '/static/icons/start-icon.svg',
                    'href': PRE_START_TRIAGE_URL,
                    'text': 'Starting a business',
                    'isCurrent': PRE_START_TRIAGE_URL in request.path,
                    'overviewText': (
                        'Get support and information'
                        '<span class="govuk-visually-hidden"> for starting a business</span>'
                    ),
                    'description': """Tell us about your plans and we'll connect you to expert guidance and
 support for setting up your business.""",
                },
                {
                    'icon': '/static/icons/run-icon.svg',
                    'href': EXISTING_TRIAGE_URL,
                    'text': 'Running and growing a business',
                    'isCurrent': EXISTING_TRIAGE_URL in request.path,
                    'overviewText': (
                        'Get support and information'
                        '<span class="govuk-visually-hidden"> for running and growing a business</span>'
                    ),
                    'description': """Tell us a bit about your business and we'll link you up to the right
 resources to help it thrive.""",
                },
                {
                    'icon': '/static/icons/export-icon.svg',
                    'href': '/export-from-uk/',
                    'text': 'Selling overseas from the UK',
                    'overviewText': 'Start exporting',
                    'children': [
                        {
                            'href': '/export-from-uk/markets/',
                            'text': 'Market guides',
                            'isCurrent': '/markets' in request.path,
                        },
                        {'href': '/export-from-uk/support-topics/', 'text': 'Export support'},
                        {
                            'href': '/export-from-uk/export-academy/',
                            'text': 'UK Export Academy',
                            'isCurrent': '/export-support/' in request.path,
                        },
                        {
                            'href': '/export-from-uk/learn/categories/',
                            'text': 'Learn to export',
                            'isCurrent': '/learn/categories/' in request.path,
                        },
                        {
                            'href': '/export-from-uk/services/',
                            'text': 'Export resources',
                            'isCurrent': '/services/' in request.path,
                        },
                        {
                            'href': '/export-from-uk/dashboard/',
                            'text': 'Export dashboard',
                            'requiresAuth': True,
                            'isCurrent': '/compare-countries' in request.path,
                        },
                        {
                            'href': reverse_lazy('core:compare-countries'),
                            'text': 'Where to export',
                            'requiresAuth': True,
                            'isCurrent': '/compare-countries' in request.path,
                        },
                        {
                            'href': '/export-from-uk/export-plan/',
                            'text': 'Make an export plan',
                            'requiresAuth': True,
                            'isCurrent': '/export-plan' in request.path,
                        },
                        {
                            'href': '/export-from-uk/profile/',
                            'text': 'Export account',
                            'requiresAuth': True,
                            'isCurrent': '/profile' in request.path,
                        },
                        {
                            'text': 'Sign out of export account services',
                            'attributes': 'onclick="signOut()"',
                            'button': True,
                            'requiresAuth': True,
                        },
                        {
                            'text': 'Sign in to export account services',
                            'href': reverse_lazy('core:login'),
                            'button': True,
                            'requiresNoAuth': True,
                        },
                    ],
                },
                {
                    'icon': '/static/icons/expand-icon.svg',
                    'href': f'/{international_url(request)}/',
                    'text': 'Investing and expanding in the UK',
                    'overviewText': 'Start investing',
                    'children': [
                        {
                            'href': f'/{international_url(request)}/expand-your-business-in-the-uk/',
                            'text': 'Expand your business in the UK',
                            'isCurrent': '/expand-your-business-in-the-uk' in request.path,
                        },
                        {
                            'href': f'/{international_url(request)}/investment/',
                            'text': 'Investment opportunities',
                            'isCurrent': (
                                f'/{international_url(request)}/investment/' == request.path
                                or (
                                    f'/{international_url(request)}/investment/' in request.path
                                    and '?back=' in request.get_full_path()
                                )
                            ),
                        },
                        {
                            'href': f'/{international_url(request)}/buy-from-the-uk/',
                            'text': 'Buy from the UK',
                            'isCurrent': '/buy-from-the-uk/' in request.path,
                        },
                        {
                            'href': '#',
                            'text': 'Sign out of expand your business in the UK',
                            'requiresAuth': True,
                            'attributes': 'onclick="signOut()"',
                        },
                        {
                            'href': reverse_lazy('international_online_offer:login'),
                            'text': 'Sign in to expand your business in the UK',
                            'requiresNoAuth': True,
                            'isCurrent': '/expand-your-business-in-the-uk/login/' in request.path,
                        },
                    ],
                },
            ],
        },
    }


def microsite_header(request):
    return {
        'rtl': get_language_bidi(),
        'include_link_to_great': '',
        'strapline': (
            'Get support for UK export or investment at '
            '<a class="great-ds-header__link" href="https://great.gov.uk">great.gov.uk</a>'
        ),
        'isCampaign': True,
        'use_domestic_logo': True,
        'site_title': '',
        'languages': '',
        'hideSearch': True,
        'hideMenuOnDesktop': True,
        'subnavItemsList': '',
        'mobileSiteLink': '',
        'bgs_header_campaign_context': {
            'rtl': get_language_bidi(),
            'hideSearch': True,
            'hideMenuOnDesktop': True,
        },
    }


def domestic_footer(request):
    return {
        'domestic_footer_context': {
            'is_international': False,
            'current_year': str(datetime.now().year),
            'logo_link_href': 'https://www.gov.uk/government/organisations/department-for-business-and-trade',
            'footer_links': [
                {
                    'href': '/support/export-support',
                    'title': 'Export support for UK businesses',
                    'text': 'Export support for UK businesses',
                },
                {
                    'href': f'/{international_url(request)}',
                    'title': 'Invest in the UK',
                    'text': 'Invest in the UK',
                },
                {
                    'href': '/contact/triage/great-account',
                    'title': 'Get help with your account',
                    'text': 'Get help with your account',
                },
                {
                    'href': '/privacy',
                    'title': 'Privacy',
                    'text': 'Privacy',
                },
                {
                    'href': '/cookies',
                    'title': 'Cookies',
                    'text': 'Cookies',
                },
                {
                    'href': '/terms-and-conditions',
                    'title': 'Terms and conditions',
                    'text': 'Terms and conditions',
                },
                {
                    'href': '/accessibility-statement',
                    'title': 'Accessibility',
                    'text': 'Accessibility',
                },
            ],
        },
    }


def international_footer(request):
    return {
        'international_footer_context': {
            'is_international': True,
            'current_year': str(datetime.now().year),
            'logo_link_href': 'https://www.gov.uk/',
            'footer_links': [
                {
                    'href': f'/{international_url(request)}/site-help/?next='
                    + request.build_absolute_uri(request.path),
                    'title': 'Help using this site',
                    'text': 'Help using this site',
                },
                {
                    'href': '/privacy',
                    'title': 'Privacy',
                    'text': 'Privacy',
                },
                {
                    'href': '/cookies',
                    'title': 'Cookies',
                    'text': 'Cookies',
                },
                {
                    'href': '/terms-and-conditions',
                    'title': 'Terms and conditions',
                    'text': 'Terms and conditions',
                },
                {
                    'href': '/accessibility-statement',
                    'title': 'Accessibility',
                    'text': 'Accessibility',
                },
                {
                    'href': '/',
                    'title': 'Export from the UK',
                    'text': 'Export from the UK',
                },
            ],
        },
    }


def microsite_footer(request):
    return {
        'is_international': False,
        'current_year': str(datetime.now().year),
        'logo_link_href': '/',
        'footer_links': [
            {
                'href': '/',
                'title': 'Export from the UK',
                'text': 'Export from the UK',
            },
            {
                'href': f'/{international_url(request)}',
                'title': 'Invest in the UK',
                'text': 'Invest in the UK',
            },
            {
                'href': '/contact/triage/great-account',
                'title': 'Get help with your account',
                'text': 'Get help with your account',
            },
            {
                'href': '/privacy',
                'title': 'Privacy',
                'text': 'Privacy',
            },
            {
                'href': '/cookies',
                'title': 'Cookies',
                'text': 'Cookies',
            },
            {
                'href': '/terms-and-conditions',
                'title': 'Terms and conditions',
                'text': 'Terms and conditions',
            },
            {
                'href': '/accessibility-statement',
                'title': 'Accessibility',
                'text': 'Accessibility',
            },
        ],
    }


def footer_bgs(request):
    return {
        'footer_bgs_context': {
            'currentYear': str(datetime.now().year),
            'upperFooterSection': [
                [
                    {
                        'href': PRE_START_TRIAGE_URL,
                        'text': 'Starting a business',
                        'title': 'Starting a business',
                        'isHeading': 'true',
                    }
                ],
                [
                    {
                        'href': EXISTING_TRIAGE_URL,
                        'text': 'Running and growing a business',
                        'title': 'Running and growing a business',
                        'isHeading': 'true',
                    }
                ],
                [
                    {
                        'href': '/export-from-uk/',
                        'text': 'Selling overseas from the UK',
                        'title': 'Selling overseas from the UK',
                        'isHeading': 'true',
                    },
                    {'href': '/export-from-uk/markets/', 'text': 'Market guides', 'title': 'Market guides'},
                    {'href': '/export-from-uk/support-topics/', 'text': 'Export support', 'title': 'Export support'},
                    {
                        'href': '/export-from-uk/export-academy/',
                        'text': 'UK Export Academy',
                        'title': 'UK Export Academy',
                    },
                    {
                        'href': '/export-from-uk/learn/categories/',
                        'text': 'Learn to export',
                        'title': 'Learn to export',
                    },
                    {'href': '/export-from-uk/services', 'text': 'Export resources', 'title': 'Export resources'},
                ],
                [
                    {
                        'href': f'/{international_url(request)}/',
                        'text': 'Investing and expanding in the UK',
                        'title': 'Investing and expanding in the UK',
                        'isHeading': 'true',
                    },
                    {
                        'href': f'/{international_url(request)}/expand-your-business-in-the-uk/',
                        'text': 'Expand your business in the UK',
                        'title': 'Expand your business in the UK',
                    },
                    {
                        'href': f'/{international_url(request)}/investment/',
                        'text': 'Investment opportunities',
                        'title': 'Investment opportunities',
                    },
                    {
                        'href': f'/{international_url(request)}/buy-from-the-uk/',
                        'text': 'Buy from the UK',
                        'title': 'Buy from the UK',
                    },
                ],
            ],
            'lowerFooterSection': [
                [
                    {'href': '/privacy/', 'text': 'Privacy', 'title': 'Privacy'},
                    {'href': '/cookies/', 'text': 'Cookies', 'title': 'Cookies'},
                    {
                        'href': '/accessibility-statement/',
                        'text': 'Accessibility statement',
                        'title': 'Accessibility statement',
                    },
                ],
                [
                    {'href': '/terms-and-conditions/', 'text': 'Terms and conditions', 'title': 'Terms and conditions'},
                    {'href': '/sitemap/', 'text': 'Sitemap', 'title': 'Sitemap'},
                ],
                [
                    {'href': '/support/', 'text': 'About this website', 'title': 'About this website'},
                    {
                        'href': '/help-using-this-website/',
                        'text': 'Help using this website',
                        'title': 'Help using this website',
                    },
                ],
                [
                    {
                        'href': 'https://www.gov.uk/government/organisations/department-for-business-and-trade',
                        'text': 'Department for Business and Trade on GOV.UK',
                        'title': 'Department for Business and Trade on GOV.UK',
                    }
                ],
            ],
        },
        'footer_bgs_microsite_context': {
            'currentYear': str(datetime.now().year),
            'upperFooterSection': [
                [
                    {'href': '/privacy/', 'text': 'Privacy', 'title': 'Privacy'},
                    {'href': '/cookies/', 'text': 'Cookies', 'title': 'Cookies'},
                    {
                        'href': '/accessibility-statement/',
                        'text': 'Accessibility statement',
                        'title': 'Accessibility statement',
                    },
                ],
                [
                    {'href': '/terms-and-conditions/', 'text': 'Terms and conditions', 'title': 'Terms and conditions'},
                    {
                        'href': f'/{international_url(request)}/site-help/?next='
                        + request.build_absolute_uri(request.path),
                        'text': 'Help using this website',
                        'title': 'Help using this website',
                    },
                ],
            ],
            'lowerFooterSection': [
                [
                    {
                        'href': '/',
                        'text': 'Find support and information for your business on Business.gov.uk',
                        'title': 'Find support and information for your business on Business.gov.uk',
                    },
                ],
                [
                    {
                        'href': 'https://www.gov.uk/government/organisations/department-for-business-and-trade',
                        'text': 'Department for Business and Trade on GOV.UK',
                        'title': 'Department for Business and Trade on GOV.UK',
                    }
                ],
            ],
        },
    }


def current_website_name(request):
    website_name = 'great.gov.uk'
    bgs_domains = ['.bgs.', 'business.gov.uk']

    for domain in bgs_domains:
        if domain in request.get_host():
            website_name = 'business.gov.uk'

    return {'current_website_name': website_name}


def bgs_chat_vars(request):
    return {'COPILOT_EMBED_SRC': settings.COPILOT_EMBED_SRC}