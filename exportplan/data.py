from django.utils.text import slugify
from django.urls import reverse_lazy


SECTION_TITLES = [
    'About your business',
    'Objectives',
    'Target markets research',
    'Adaptation for your target market',
    'Marketing approach',
    'Costs and pricing',
    'Finance',
    'Payment methods',
    'Travel and business policies',
    'Business risk',
]

SECTION_SLUGS = [slugify(section) for section in SECTION_TITLES]

SECTION_URLS = [reverse_lazy('exportplan:section', kwargs={'slug': slug}) for slug in SECTION_SLUGS]

SECTION_TITLES_URLS = [
    {
        'title': section,
        'url': reverse_lazy('exportplan:section', kwargs={'slug': slugify(section)})
    } for section in SECTION_TITLES
]

# Note that SECTION_TITLES_URLS can't be rearranged into a dictionary while preserving
# the lazy URL reversal, so manipulating SECTION_TITLES_URLS needs to happen after the
# app is ready to avoid django.core.exceptions.AppRegistryNotReady
