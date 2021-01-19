import factory
import factory.fuzzy
import wagtail_factories

from core import blocks as core_blocks, constants
from domestic.models import (
    ArticlePage,
    CountryGuidePage,
    DomesticDashboard,
    DomesticHomePage,
)


class RouteSectionFactory(wagtail_factories.StructBlockFactory):
    title = 'Title'
    route_type = 'learn'
    body = factory.fuzzy.FuzzyText(length=60)
    image = None
    button = None

    class Meta:
        model = core_blocks.RouteSectionBlock


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'homepage'
    body = factory.fuzzy.FuzzyText(length=255)
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticHomePage


class DomesticDashboardFactory(wagtail_factories.PageFactory):
    title = 'Title of Dashboard'
    live = True
    slug = 'dashboard'

    components = wagtail_factories.StreamFieldFactory({'route': RouteSectionFactory})

    class Meta:
        model = DomesticDashboard


class CountryGuidePageFactory(wagtail_factories.PageFactory):
    title = 'Title of Country'
    heading = 'Heading for Country'
    hero_image = factory.SubFactory(
        wagtail_factories.ImageChooserBlockFactory,
    )
    section_one_body = 'Section one body lorem ipsum'
    section_one_image = factory.SubFactory(
        wagtail_factories.ImageChooserBlockFactory,
    )
    live = True

    class Meta:
        model = CountryGuidePage


class ArticlePageFactory(wagtail_factories.PageFactory):

    type_of_article = constants.ARTICLE_TYPES[1][0]
    article_body_text = factory.fuzzy.FuzzyText(length=255)

    class Meta:
        model = ArticlePage
