from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import (
    ArticleListingPage,
    ArticlePage,
    CountryGuidePage,
    DomesticDashboard,
    GreatDomesticHomePage,
    GuidancePage,
    ManuallyConfigurableTopicLandingPage,
    MarketsTopicLandingPage,
    PerformanceDashboardPage,
    StructuralPage,
    TopicLandingBasePage,
    TopicLandingPage,
    TradeFinancePage,
)


@register(ArticlePage)
class ArticlePageTO(TranslationOptions):
    fields = ()


@register(ArticleListingPage)
class ArticleListingPageTO(TranslationOptions):
    fields = ()


@register(PerformanceDashboardPage)
class PerformanceDashboardPageTO(TranslationOptions):
    fields = ()


@register(TopicLandingBasePage)
class TopicLandingBasePageTO(TranslationOptions):
    fields = ()


@register(TopicLandingPage)
class TopicLandingPageTO(TranslationOptions):
    fields = ()


@register(GreatDomesticHomePage)
class GreatDomesticHomePageTO(TranslationOptions):
    fields = ()


@register(StructuralPage)
class StructuralPageTO(TranslationOptions):
    fields = ()


@register(MarketsTopicLandingPage)
class MarketsTopicLandingPageTO(TranslationOptions):
    fields = ()


@register(DomesticDashboard)
class DomesticDashboardTO(TranslationOptions):
    fields = ()


@register(GuidancePage)
class GuidancePageTO(TranslationOptions):
    fields = ()


@register(TradeFinancePage)
class TradeFinancePageTO(TranslationOptions):
    fields = ()


@register(ManuallyConfigurableTopicLandingPage)
class ManuallyConfigurableTO(TranslationOptions):
    fields = ()


@register(CountryGuidePage)
class CountryGuidePageTO(TranslationOptions):
    fields = ()
