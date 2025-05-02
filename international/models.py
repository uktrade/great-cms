from django.db import models
from wagtail.fields import StreamBlock, StreamField

from core.blocks import SupportTopicCardBlock
from domestic.models import BaseContentPage
from international import cms_panels


class GreatInternationalHomePage(cms_panels.GreatInternationalHomePagePanels, BaseContentPage):
    #  This is the main homepge for Great.gov.uk/international

    parent_page_types = [
        'domestic.GreatDomesticHomePage',
    ]

    template = 'international/index.html'

    # hero
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_mobile_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_text = models.TextField(null=True, blank=True)
    hero_subtitle = models.TextField(null=True, blank=True)

    dep_title = models.TextField(null=True, blank=True)
    dep_sub_title = models.TextField(null=True, blank=True)

    dep_cards = StreamField(
        [
            (
                'cards',
                StreamBlock(
                    [
                        ('topic_card', SupportTopicCardBlock()),
                    ],
                    block_counts={
                        'topic_card': {'min_num': 1},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['eyb_card_attributes'] = {
            'data_attr_location': 'International homepage',
            'data_attr_title': 'How to expand your business',
        }
        context['investment_card_attributes'] = {
            'data_attr_location': 'International homepage',
            'data_attr_title': 'Find investment opportunities',
        }
        context['buy_from_uk_card_attributes'] = {
            'data_attr_location': 'International homepage',
            'data_attr_title': 'Buy UK products and services',
        }
        return context

    


class Sector(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
