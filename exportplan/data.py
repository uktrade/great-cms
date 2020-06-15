from django.utils.text import slugify
from django.urls import reverse_lazy


SECTION_TITLES = [
    'Brand and product',
    'Objectives',
    'Target markets',
    'Adaptation for international markets',
    'Marketing approach',
    'Costs and pricing',
    'Finance',
    'Payment methods',
    'Travel and business policies',
    'Business risk',
]

SECTION_SLUGS = [slugify(section) for section in SECTION_TITLES]

SECTION_URLS = [reverse_lazy('exportplan:section', kwargs={'slug': slug}) for slug in SECTION_SLUGS]
