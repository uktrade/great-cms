from django.utils.text import slugify
from django.urls import reverse_lazy


SECTION_TITLES = [
    'About your business',
    'Objectives',
    'Target markets',
    'Adaptation for international markets',
    'Marketing approach',
    'Finance',
    'Costs and pricing',
    'Payment methods',
    'Travel and business policies',
    'Business risk',
    'Action plan',
]

SECTION_SLUGS = [slugify(section) for section in SECTION_TITLES]

SECTION_URLS = [reverse_lazy('exportplan:section', kwargs={'slug': slug}) for slug in SECTION_SLUGS]
