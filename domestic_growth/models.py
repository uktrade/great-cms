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


class DomesticGrowthHomePage(SeoMixin, cms_panels.DomesticGrowthHomePagePanels, Page):
    template = 'home.html'

    class Meta:
        verbose_name = 'Domestic Growth Home page'

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_title = models.TextField(
        null=True,
    )

    hero_intro = models.TextField(
        null=True,
    )

    explore_title = models.TextField(
        null=True,
        blank=True,
    )

    explore_body = StreamField(
        [
            (
                'explore_cards',
                StreamBlock(
                    [
                        ('explore_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'explore_card': {'min_num': 4},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    guidance_title = models.TextField(
        null=True,
    )

    guidance_body = StreamField(
        [
            (
                'guidance_cards',
                StreamBlock(
                    [
                        ('guidance_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'guidance_card': {'min_num': 4},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    about_title = models.TextField(
        null=True,
    )

    about_intro = models.TextField(
        null=True,
    )

    about_description = models.TextField(
        null=True,
    )

    news_title = models.TextField(
        null=True,
    )

    news_link_text = models.TextField(
        null=True,
    )

    news_link_url = models.TextField(
        null=True,
    )

    feedback_title = models.TextField(
        null=True,
    )

    feedback_description = models.TextField(
        null=True,
    )

    feedback_link_text = models.TextField(
        null=True,
    )

    feedback_link_url = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthHomePage, self).get_context(request)
        context['news'] = helpers.get_dbt_news_articles()
        return context
