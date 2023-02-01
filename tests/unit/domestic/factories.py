import factory
import factory.fuzzy
import wagtail_factories
from django.utils import timezone

from core import blocks as core_blocks, constants, service_urls
from domestic.models import (
    ArticleListingPage,
    ArticlePage,
    CountryGuidePage,
    DomesticDashboard,
    DomesticHomePage,
    GreatDomesticHomePage,
    ManuallyConfigurableTopicLandingPage,
    MarketsTopicLandingPage,
    PerformanceDashboardPage,
    TopicLandingPage,
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
    # This is the MVP Magna homepage for private beta
    title = 'homepage'
    body = factory.fuzzy.FuzzyText(length=255)
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticHomePage


class GreatDomesticHomePageFactory(wagtail_factories.PageFactory):
    # This is the MVP Magna homepage for private beta
    title = 'homepage'
    live = True
    slug = 'homepage'
    magna_ctas_columns = []

    class Meta:
        model = GreatDomesticHomePage


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


class ArticleListingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ArticleListingPage


class ArticlePageFactory(wagtail_factories.PageFactory):
    type_of_article = constants.ARTICLE_TYPES[1][0]
    last_published_at = timezone.now()

    class Meta:
        model = ArticlePage


class TopicLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = TopicLandingPage


class MarketsTopicLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = MarketsTopicLandingPage


class PerformanceDashboardPageFactory(wagtail_factories.PageFactory):
    product_link = service_urls.SERVICES_GREAT_DOMESTIC
    description = factory.fuzzy.FuzzyText(length=60)

    class Meta:
        model = PerformanceDashboardPage


class ManuallyConfigurableTopicLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ManuallyConfigurableTopicLandingPage
