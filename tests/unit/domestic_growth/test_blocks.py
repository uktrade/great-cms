from wagtail import blocks

from domestic_growth.models import DomesticGrowthCardBlock


def test_card_block():
    assert issubclass(DomesticGrowthCardBlock, blocks.StructBlock)
