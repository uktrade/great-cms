from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from core import blocks as core_blocks


class CampaignBlock(core_blocks.LinkBlock):
    heading = blocks.CharBlock()
    subheading = blocks.CharBlock()
    image = ImageChooserBlock()


class MarketAccessDBBlock(core_blocks.LinkWithImageAndContentBlock):
    title = blocks.CharBlock()
