from django.db import models
from domestic_growth import (
    cms_panels,
)
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtailseo.models import SeoMixin
from domestic_growth.blocks import DomesticGrowthCardBlock


class DomesticGrowthLandingPage(SeoMixin, cms_panels.DomesticGrowthLandingPagePanels, Page):
    template = 'landing.html'

    class Meta:
        verbose_name = 'Domestic Growth Landing page'

    hero_title = models.TextField(
        null=True,
    )

    hero_body = StreamField(
        [
            (
                'hero_cards',
                StreamBlock(
                    [
                        ('hero_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'hero_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )
