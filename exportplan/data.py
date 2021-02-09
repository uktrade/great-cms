from collections import OrderedDict

from django.urls import reverse_lazy
from django.utils.text import slugify

from config import settings

# Constants
ABOUT_YOUR_BUSINESS = 'About your business'
OBJECTIVES = 'Business objectives'
TARGET_MARKETS_RESEARCH = 'Target markets research'
ADAPTATION_TARGET_MARKET = 'Adaptation for your target market'
MARKETING_APPROACH = 'Marketing approach'
COSTS_AND_PRICING = 'Costs and pricing'
GETTING_PAID = 'Getting paid'
FUNDING_AND_CREDIT = 'Funding and Credit'
PAYMENT_METHODS = 'Payment methods'
TRAVEL_AND_BUSINESS_POLICIES = 'Travel and business policies'
BUSINESS_RISK = 'Business risk'


# This Map is used to enabled/disable sections on export plan
SECTIONS_DISABLED = settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED_LIST

# This maintains a collection of which pages require a country to be selected
COUNTRY_REQUIRED = [
    slugify(TARGET_MARKETS_RESEARCH),
    slugify(ADAPTATION_TARGET_MARKET),
    slugify(MARKETING_APPROACH),
    slugify(COSTS_AND_PRICING),
    slugify(GETTING_PAID),
    slugify(FUNDING_AND_CREDIT),
    slugify(PAYMENT_METHODS),
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
]

# This maintains a collection of which pages require a country to be selected
PRODUCT_REQUIRED = [
    slugify(TARGET_MARKETS_RESEARCH),
    slugify(ADAPTATION_TARGET_MARKET),
    slugify(MARKETING_APPROACH),
    slugify(COSTS_AND_PRICING),
    slugify(FUNDING_AND_CREDIT),
    slugify(PAYMENT_METHODS),
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
    slugify(BUSINESS_RISK),
]

# This maintains a collection of which pages require a lesson, the order of these lessons corresponds to the order
# on the UI page

LESSONS = {
    OBJECTIVES: ['opportunity-right-you', 'move-accidental-exporting-strategic-exporting'],
    MARKETING_APPROACH: ['sell-direct-your-customer'],
    TARGET_MARKETS_RESEARCH: [
        'quantifying-customer-demand-how-much-might-you-sell',
        'using-what-you-know-to-help-inform-your-positioning-and-competitive-advantage',
        'understand-market-trends',
    ],
    COSTS_AND_PRICING: [
        'understand-services-rules-and-regulations',
        'understand-services-rules-and-regulations',
        'managing-exchange-rates',
    ],
}

SECTIONS = OrderedDict(
    {
        slugify(ABOUT_YOUR_BUSINESS): {
            'title': ABOUT_YOUR_BUSINESS,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(ABOUT_YOUR_BUSINESS)}),
            'disabled': True if ABOUT_YOUR_BUSINESS in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(ABOUT_YOUR_BUSINESS, []),
        },
        slugify(OBJECTIVES): {
            'title': OBJECTIVES,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(OBJECTIVES)}),
            'disabled': True if OBJECTIVES in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(OBJECTIVES, []),
        },
        slugify(TARGET_MARKETS_RESEARCH): {
            'title': TARGET_MARKETS_RESEARCH,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(TARGET_MARKETS_RESEARCH)}),
            'disabled': True if TARGET_MARKETS_RESEARCH in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(TARGET_MARKETS_RESEARCH, []),
        },
        slugify(ADAPTATION_TARGET_MARKET): {
            'title': ADAPTATION_TARGET_MARKET,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(ADAPTATION_TARGET_MARKET)}),
            'disabled': True if ADAPTATION_TARGET_MARKET in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(ADAPTATION_TARGET_MARKET, []),
        },
        slugify(MARKETING_APPROACH): {
            'title': MARKETING_APPROACH,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(MARKETING_APPROACH)}),
            'disabled': True if MARKETING_APPROACH in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(MARKETING_APPROACH, []),
        },
        slugify(COSTS_AND_PRICING): {
            'title': COSTS_AND_PRICING,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(COSTS_AND_PRICING)}),
            'disabled': True if COSTS_AND_PRICING in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(COSTS_AND_PRICING, []),
        },
        slugify(FUNDING_AND_CREDIT): {
            'title': FUNDING_AND_CREDIT,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(FUNDING_AND_CREDIT)}),
            'disabled': True if FUNDING_AND_CREDIT in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(FUNDING_AND_CREDIT, []),
        },
        slugify(GETTING_PAID): {
            'title': GETTING_PAID,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(GETTING_PAID)}),
            'disabled': True if GETTING_PAID in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(GETTING_PAID, []),
        },
        slugify(TRAVEL_AND_BUSINESS_POLICIES): {
            'title': TRAVEL_AND_BUSINESS_POLICIES,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(TRAVEL_AND_BUSINESS_POLICIES)}),
            'disabled': True if TRAVEL_AND_BUSINESS_POLICIES in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(TRAVEL_AND_BUSINESS_POLICIES, []),
        },
        slugify(BUSINESS_RISK): {
            'title': BUSINESS_RISK,
            'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(BUSINESS_RISK)}),
            'disabled': True if BUSINESS_RISK in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(BUSINESS_RISK, []),
        },
    }
)


SECTION_TITLES = [val['title'] for val in SECTIONS.values()]
SECTION_SLUGS = list(SECTIONS.keys())
SECTION_URLS = list(SECTIONS.values())

# Note that SECTION_TITLES_URLS can't be rearranged into a dictionary while preserving
# the lazy URL reversal, so manipulating SECTION_TITLES_URLS needs to happen after the
# app is ready to avoid django.core.exceptions.AppRegistryNotReady
