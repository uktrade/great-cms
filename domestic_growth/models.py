from django.db import models
from domestic_growth import (
    cms_panels,
)
from wagtail.models import Page
from wagtailseo.models import SeoMixin


class DomesticGrowthLandingPage(SeoMixin, cms_panels.DomesticGrowthLandingPagePanels, Page):
    template = 'landing.html'

    class Meta:
        verbose_name = 'Domestic Growth Landing page'

    hero_title = models.TextField(
        null=True,
    )
