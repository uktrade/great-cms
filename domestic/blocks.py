from wagtail.core import blocks
from core import blocks as core_blocks


class CampaignBlock(core_blocks.ImageBaseBlock, core_blocks.LinkBlock):
    heading = blocks.CharBlock()
    subheading = blocks.CharBlock()


class MarketAccessDBBlock(core_blocks.LinkWithImageAndContentBlock):
    title = blocks.CharBlock()
