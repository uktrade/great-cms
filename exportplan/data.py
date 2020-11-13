from django.utils.text import slugify
from django.urls import reverse_lazy
from config import settings
from collections import OrderedDict

# Constants
ABOUT_YOUR_BUSINESS = 'About your business'
OBJECTIVES = 'Business objectives'
TARGET_MARKETS_RESEARCH = 'Target markets research'
ADAPTATION_TARGET_MARKET = 'Adaptation for your target market'
MARKETING_APPROACH = 'Marketing approach'
COSTS_AND_PRICING = 'Costs and pricing'
FINANCE = 'Finance'
PAYMENT_METHODS = 'Payment methods'
TRAVEL_AND_BUSINESS_POLICIES = 'Travel and business policies'
BUSINESS_RISK = 'Business risk'


if settings.FEATURE_EXPORT_PLAN_SECTIONS_DISABLED:
    # This Map is used to enabled/disable sections on export plan
    SECTIONS_DISABLED = [
        TARGET_MARKETS_RESEARCH,
        ADAPTATION_TARGET_MARKET,
        COSTS_AND_PRICING,
        FINANCE,
        PAYMENT_METHODS,
        TRAVEL_AND_BUSINESS_POLICIES,
        BUSINESS_RISK,
    ]
else:
    SECTIONS_DISABLED = []

# This maintains a collection of which pages require a country to be selected
COUNTRY_REQUIRED = [
    slugify(TARGET_MARKETS_RESEARCH),
    slugify(ADAPTATION_TARGET_MARKET),
    slugify(MARKETING_APPROACH),
    slugify(COSTS_AND_PRICING),
    slugify(FINANCE),
    slugify(PAYMENT_METHODS),
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
]

# This maintains a collection of which pages require a country to be selected
PRODUCT_REQUIRED = [
    slugify(TARGET_MARKETS_RESEARCH),
    slugify(ADAPTATION_TARGET_MARKET),
    slugify(MARKETING_APPROACH),
    slugify(COSTS_AND_PRICING),
    slugify(FINANCE),
    slugify(PAYMENT_METHODS),
    slugify(TRAVEL_AND_BUSINESS_POLICIES),
    slugify(BUSINESS_RISK),
]

SECTIONS = OrderedDict({
    slugify(ABOUT_YOUR_BUSINESS): {
        'title': ABOUT_YOUR_BUSINESS,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(ABOUT_YOUR_BUSINESS)}),
        'disabled': True if ABOUT_YOUR_BUSINESS in SECTIONS_DISABLED else False,
    },
    slugify(OBJECTIVES): {
        'title': OBJECTIVES,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(OBJECTIVES)}),
        'disabled': True if OBJECTIVES in SECTIONS_DISABLED else False,
    },
    slugify(TARGET_MARKETS_RESEARCH): {
        'title': TARGET_MARKETS_RESEARCH,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(TARGET_MARKETS_RESEARCH)}),
        'disabled': True if TARGET_MARKETS_RESEARCH in SECTIONS_DISABLED else False,
    },
    slugify(ADAPTATION_TARGET_MARKET): {
        'title': ADAPTATION_TARGET_MARKET,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(ADAPTATION_TARGET_MARKET)}),
        'disabled': True if ADAPTATION_TARGET_MARKET in SECTIONS_DISABLED else False,
    },
    slugify(MARKETING_APPROACH): {
        'title': MARKETING_APPROACH,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(MARKETING_APPROACH)}),
        'disabled': True if MARKETING_APPROACH in SECTIONS_DISABLED else False,
    },
    slugify(COSTS_AND_PRICING): {
        'title': COSTS_AND_PRICING,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(COSTS_AND_PRICING)}),
        'disabled': True if COSTS_AND_PRICING in SECTIONS_DISABLED else False,
    },
    slugify(FINANCE): {
        'title': FINANCE,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(FINANCE)}),
        'disabled': True if FINANCE in SECTIONS_DISABLED else False,
    },
    slugify(PAYMENT_METHODS): {
        'title': PAYMENT_METHODS,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(PAYMENT_METHODS)}),
        'disabled': True if PAYMENT_METHODS in SECTIONS_DISABLED else False,
    },
    slugify(TRAVEL_AND_BUSINESS_POLICIES): {
        'title': TRAVEL_AND_BUSINESS_POLICIES,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(TRAVEL_AND_BUSINESS_POLICIES)}),
        'disabled': True if TRAVEL_AND_BUSINESS_POLICIES in SECTIONS_DISABLED else False,
    },
    slugify(BUSINESS_RISK): {
        'title': BUSINESS_RISK,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(BUSINESS_RISK)}),
        'disabled': True if BUSINESS_RISK in SECTIONS_DISABLED else False,
    },
})


SECTION_TITLES = [val['title'] for val in SECTIONS.values()]
SECTION_SLUGS = list(SECTIONS.keys())
SECTION_URLS = list(SECTIONS.values())

# Note that SECTION_TITLES_URLS can't be rearranged into a dictionary while preserving
# the lazy URL reversal, so manipulating SECTION_TITLES_URLS needs to happen after the
# app is ready to avoid django.core.exceptions.AppRegistryNotReady
