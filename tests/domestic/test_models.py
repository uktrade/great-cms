from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from core import blocks as core_blocks
from core import mixins
from domestic.models import DomesticHomePage
from domestic import blocks as domestic_blocks


class DomesticHomePageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(DomesticHomePage, {Page})

    def test_hero_streamfield(self):
        assert DomesticHomePage.hero.field.name == 'hero'
        blocks = DomesticHomePage().hero.stream_block.child_blocks
        assert type(blocks['hero']) is core_blocks.HeroBlock

    def test_market_access_db_streamfield(self):
        assert DomesticHomePage.market_access_db.field.name == 'market_access_db'
        blocks = DomesticHomePage().market_access_db.stream_block.child_blocks
        assert type(blocks['market_access_db']) is domestic_blocks.MarketAccessDBBlock

    def test_campaign_streamfield(self):
        assert DomesticHomePage.campaign.field.name == 'campaign'
        blocks = DomesticHomePage().campaign.stream_block.child_blocks
        assert type(blocks['campaign']) is domestic_blocks.CampaignBlock

    def test_page_is_exclusive(self):
        assert issubclass(DomesticHomePage, mixins.WagtailAdminExclusivePageMixin)
