from django.db import models
from domestic_growth import (
    cms_panels,
    helpers,
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

    support_title = models.TextField(
        null=True,
    )

    support_body = StreamField(
        [
            (
                'support_cards',
                StreamBlock(
                    [
                        ('support_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'support_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    popular_title = models.TextField(
        null=True,
    )

    popular_body = StreamField(
        [
            (
                'popular_cards',
                StreamBlock(
                    [
                        ('popular_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'popular_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    news_title = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthLandingPage, self).get_context(request)
        context['news'] = helpers.get_dbt_news_articles()
        return context
