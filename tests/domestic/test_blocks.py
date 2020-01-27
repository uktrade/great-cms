from wagtail.core import blocks

from core import blocks as core_blocks
from domestic import blocks as domestic_blocks


def test_campaign_block():
    assert issubclass(
        domestic_blocks.CampaignBlock,
        (core_blocks.ImageBaseBlock, core_blocks.LinkBlock)
    )
    child_blocks = domestic_blocks.CampaignBlock().child_blocks
    assert type(child_blocks['heading']) is blocks.CharBlock
    assert type(child_blocks['subheading']) is blocks.CharBlock


def test_market_access_db_block():
    assert issubclass(domestic_blocks.MarketAccessDBBlock, core_blocks.LinkWithImageAndContentBlock)
    child_blocks = domestic_blocks.MarketAccessDBBlock().child_blocks
    assert type(child_blocks['title']) is blocks.CharBlock
