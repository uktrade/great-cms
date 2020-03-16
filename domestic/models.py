from wagtail.admin.edit_handlers import StreamFieldPanel

from wagtail.core.models import Page

from core import fields, mixins
from core import blocks as core_blocks
from domestic import blocks


class DomesticHomePage(
    mixins.WagtailAdminExclusivePageMixin,
    mixins.EnableTourMixin,
    mixins.AnonymousUserRequired,
    Page,
):
    parent_page_types = ['wagtailcore.Page']

    hero = fields.single_struct_block_stream_field_factory(
        field_name='hero',
        block_class_instance=core_blocks.HeroBlock(),
        max_num=1, null=True, blank=True
    )
    market_access_db = fields.single_struct_block_stream_field_factory(
        field_name='market_access_db',
        block_class_instance=blocks.MarketAccessDBBlock(),
        max_num=1, null=True, blank=True
    )

    campaign = fields.single_struct_block_stream_field_factory(
        field_name='campaign',
        block_class_instance=blocks.CampaignBlock(),
        max_num=1, null=True, blank=True
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('hero'),
        StreamFieldPanel('market_access_db'),
        StreamFieldPanel('campaign')
    ]
