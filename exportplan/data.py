from django.utils.text import slugify
from django.urls import reverse_lazy
from config import settings

# Constants
ABOUT_YOUR_BUSINESS = 'About your business'
OBJECTIVES = 'Objectives'
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
        MARKETING_APPROACH,
        COSTS_AND_PRICING,
        FINANCE,
        PAYMENT_METHODS,
        TRAVEL_AND_BUSINESS_POLICIES,
        BUSINESS_RISK,
    ]
else:
    SECTIONS_DISABLED = []


SECTION_TITLES = [
    ABOUT_YOUR_BUSINESS,
    OBJECTIVES,
    TARGET_MARKETS_RESEARCH,
    ADAPTATION_TARGET_MARKET,
    MARKETING_APPROACH,
    COSTS_AND_PRICING,
    FINANCE,
    PAYMENT_METHODS,
    TRAVEL_AND_BUSINESS_POLICIES,
    BUSINESS_RISK,
]

SECTION_SLUGS = [slugify(section) for section in SECTION_TITLES]
SECTIONS_DISABLED_SLUGS = [slugify(section) for section in SECTIONS_DISABLED]

SECTION_URLS = [reverse_lazy('exportplan:section', kwargs={'slug': slug}) for slug in SECTION_SLUGS]

SECTION_TITLES_URLS = [
    {
        'title': section,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(section)}),
        'disabled': True if section in SECTIONS_DISABLED else False,
    } for section in SECTION_TITLES
]


# Note that SECTION_TITLES_URLS can't be rearranged into a dictionary while preserving
# the lazy URL reversal, so manipulating SECTION_TITLES_URLS needs to happen after the
# app is ready to avoid django.core.exceptions.AppRegistryNotReady
