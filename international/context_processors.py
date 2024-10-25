from django.urls import reverse_lazy

from international_online_offer.context_processors import (
    hide_primary_nav,
    user_completed_triage,
)


def international_header(request):
    search_icon = (
        '<svg xmlns="http://www.w3.org/2000/svg" class="great-ds-icon--svg" width="20" height="20" '
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
        '<svg class="great-ds-icon--svg great-ds-icon--menu" width="16" height="17" viewBox="0 0 16 17" '
        'xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" class="great-ds-icon--menu-bars" '
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

    is_authenticated = is_authenticated = getattr(getattr(request, 'user', None), 'is_authenticated', False)
    site_title_href = '/international/expand-your-business-in-the-uk/'

    if is_authenticated:
        site_title_href = '/international/expand-your-business-in-the-uk/guide/'

    site_title = {
        'text': 'Expand your business in the UK',
        'href': site_title_href,
    }

    if not hide_primary_nav(request)['hide_primary_nav']:
        site_title = None

    return {
        'international_header_context': {
            'header_classes': '',
            'isInternational': True,
            'sso_is_logged_in': is_authenticated,
            'isAuthenticated': is_authenticated,
            'hideSearch': True,
            'hideMenuOnDesktop': True,
            'use_domestic_logo': False,
            'hideMainNav': hide_primary_nav(request)['hide_primary_nav'],
            'siteTitle': site_title,
            'domesticLink': {'href': '/', 'text': 'Export from the UK'},
            'internationalLink': {'href': '/international/', 'text': 'Invest in the UK'},
            'searchFormAction': reverse_lazy('search:search'),
            'navItemsList': [
                {
                    'href': '/international/expand-your-business-in-the-uk/',
                    'text': 'Expand your business',
                    'location': 'International header',
                    'isCurrent': '/expand-your-business-in-the-uk' in request.path,
                    'navItemsListChildren': [
                        {
                            'href': reverse_lazy('international_online_offer:login'),
                            'text': 'Sign in',
                            'location': 'EYB sub-nav',
                            'requiresNoAuth': True,
                            'isCurrent': '/expand-your-business-in-the-uk/login/' in request.path,
                        },
                        {
                            'href': reverse_lazy('international_online_offer:change-your-answers'),
                            'text': 'Your details',
                            'location': 'EYB sub-nav',
                            'requiresAuth': user_completed_triage(request),
                            'isCurrent': '/expand-your-business-in-the-uk/change-your-answers' in request.path,
                        },
                        {
                            'text': 'Sign out',
                            'location': 'EYB sub-nav',
                            'href': '#',
                            'attributes': 'onclick="signOut()"',
                            'requiresAuth': True,
                        },
                    ],
                },
                {
                    'href': '/international/investment/opportunities/',
                    'text': 'Investment opportunities',
                    'location': 'International header',
                    'isCurrent': '/international/investment/' in request.path,
                },
                {
                    'href': '/international/buy-from-the-uk/',
                    'text': 'Buy from the UK',
                    'location': 'International header',
                    'isCurrent': '/international/buy-from-the-uk/' in request.path,
                },
            ],
            'menuItemsList': [
                {
                    'href': '/international/expand-your-business-in-the-uk/',
                    'location': 'International header',
                    'text': 'Expand your business',
                    'isCurrent': '/expand-your-business-in-the-uk' in request.path,
                },
                {
                    'href': '/international/investment/opportunities/',
                    'text': 'Investment opportunities',
                    'location': 'International header',
                    'isCurrent': '/international/investment/' in request.path,
                },
                {
                    'href': '/international/buy-from-the-uk/',
                    'text': 'Buy from the UK',
                    'location': 'International header',
                    'isCurrent': '/international/buy-from-the-uk/' in request.path,
                },
            ],
            'mobileSiteLink': {'href': '/', 'text': 'Export from the UK'},
            'search_icon': search_icon,
            'menu_icon': menu_icon,
        }
    }
