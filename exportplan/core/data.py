from collections import OrderedDict

from django.utils.text import slugify

from config import settings

# Constants
ABOUT_YOUR_BUSINESS = 'About your business'
OBJECTIVES = 'Business objectives'
TARGET_MARKETS_RESEARCH = 'Target markets research'
ADAPTATION_TARGET_MARKET = 'Adapting your product'
MARKETING_APPROACH = 'Marketing approach'
COSTS_AND_PRICING = 'Costs and pricing'
GETTING_PAID = 'Getting paid'
FUNDING_AND_CREDIT = 'Funding and credit'
TRAVEL_AND_BUSINESS_POLICIES = 'Travel plan'
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
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
]

# This maintains a collection of which pages require a country to be selected
PRODUCT_REQUIRED = [
    slugify(TARGET_MARKETS_RESEARCH),
    slugify(ADAPTATION_TARGET_MARKET),
    slugify(MARKETING_APPROACH),
    slugify(COSTS_AND_PRICING),
    slugify(FUNDING_AND_CREDIT),
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
    slugify(BUSINESS_RISK),
]

# This maintains a collection of which pages require a lesson, the order of these lessons corresponds to the order
# on the UI page

LESSONS = {
    OBJECTIVES: ['move-accidental-exporting-strategic-exporting'],
    MARKETING_APPROACH: [
        'choose-right-route-market',
    ],
    TARGET_MARKETS_RESEARCH: [
        'quantifying-customer-demand-how-much-might-you-sell',
        'understanding-competitor-market-share-and-pricing',
    ],
    COSTS_AND_PRICING: [
        'understand-duties-and-taxes',
        'understand-duties-and-taxes',
        'managing-exchange-rates',
    ],
    FUNDING_AND_CREDIT: [
        'how-avoid-cashflow-challenges-when-exporting',
        'funding-and-credit-options-doing-business-across-borders',
    ],
    GETTING_PAID: [
        'payment-methods-exporters',
        'decide-when-get-paid-export-orders',
        'incoterms',
    ],
    ADAPTATION_TARGET_MARKET: [
        'understand-how-you-may-need-adapt-your-product-meet-international-standards',
        'labelling-and-packaging',
        'labelling-and-packaging',
        'understand-local-market-regulations-products',
        'understand-export-licensing',
        'how-create-export-invoice',
        'how-make-uk-customs-declaration',
    ],
    TRAVEL_AND_BUSINESS_POLICIES: ['understand-local-business-culture-your-target-market'],
    BUSINESS_RISK: ['protect-your-intellectual-property-abroad'],
}


SECTIONS = OrderedDict(
    {
        slugify(ABOUT_YOUR_BUSINESS): {
            'title': ABOUT_YOUR_BUSINESS,
            'disabled': True if ABOUT_YOUR_BUSINESS in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(ABOUT_YOUR_BUSINESS, []),
            'image': 'about-the-business.png',
        },
        slugify(OBJECTIVES): {
            'title': OBJECTIVES,
            'disabled': True if OBJECTIVES in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(OBJECTIVES, []),
            'image': 'business-objectives.png',
        },
        slugify(TARGET_MARKETS_RESEARCH): {
            'title': TARGET_MARKETS_RESEARCH,
            'disabled': True if TARGET_MARKETS_RESEARCH in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(TARGET_MARKETS_RESEARCH, []),
            'image': 'target-market-research.png',
        },
        slugify(ADAPTATION_TARGET_MARKET): {
            'title': ADAPTATION_TARGET_MARKET,
            'disabled': True if ADAPTATION_TARGET_MARKET in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(ADAPTATION_TARGET_MARKET, []),
            'image': 'funding-financing-and--getting-paid.png',
        },
        slugify(MARKETING_APPROACH): {
            'title': MARKETING_APPROACH,
            'disabled': True if MARKETING_APPROACH in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(MARKETING_APPROACH, []),
            'image': 'marketing-approach.png',
        },
        slugify(COSTS_AND_PRICING): {
            'title': COSTS_AND_PRICING,
            'disabled': True if COSTS_AND_PRICING in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(COSTS_AND_PRICING, []),
            'image': 'costs-and-pricing.png',
        },
        slugify(FUNDING_AND_CREDIT): {
            'title': FUNDING_AND_CREDIT,
            'disabled': True if FUNDING_AND_CREDIT in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(FUNDING_AND_CREDIT, []),
            'image': 'funding-and-credit.png',
        },
        slugify(GETTING_PAID): {
            'title': GETTING_PAID,
            'disabled': True if GETTING_PAID in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(GETTING_PAID, []),
            'image': 'getting-paid.png',
        },
        slugify(TRAVEL_AND_BUSINESS_POLICIES): {
            'title': TRAVEL_AND_BUSINESS_POLICIES,
            'disabled': True if TRAVEL_AND_BUSINESS_POLICIES in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(TRAVEL_AND_BUSINESS_POLICIES, []),
            'image': 'travel-plan.png',
        },
        slugify(BUSINESS_RISK): {
            'title': BUSINESS_RISK,
            'disabled': True if BUSINESS_RISK in SECTIONS_DISABLED else False,
            'lessons': LESSONS.get(BUSINESS_RISK, []),
            'image': 'business-risk.png',
        },
    }
)


SECTION_TITLES = [val['title'] for val in SECTIONS.values()]
SECTION_SLUGS = list(SECTIONS.keys())
SECTION_URLS = list(SECTIONS.values())

# Note that SECTION_TITLES_URLS can't be rearranged into a dictionary while preserving
# the lazy URL reversal, so manipulating SECTION_TITLES_URLS needs to happen after the
# app is ready to avoid django.core.exceptions.AppRegistryNotReady
