import factory
import factory.fuzzy
import wagtail_factories
from django.utils.text import slugify

from core import blocks, models
from tests.unit.domestic.factories import DomesticHomePageFactory


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('word')

    class Meta:
        model = models.Product


class CountryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda x: slugify(x.name))

    class Meta:
        model = models.Country
        django_get_or_create = ['slug']


class ContentModuleFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('word')

    class Meta:
        model = models.ContentModule


class LandingPageFactory(wagtail_factories.PageFactory):
    title = 'Landing page'
    description = factory.fuzzy.FuzzyText(length=200)
    template = factory.fuzzy.FuzzyChoice(models.LandingPage.template_choices, getter=lambda choice: choice[0])
    parent = factory.SubFactory(DomesticHomePageFactory)

    class Meta:
        model = models.LandingPage
        django_get_or_create = ['slug', 'parent']


class InterstitialPageFactory(wagtail_factories.PageFactory):
    title = 'Interstitial page'
    template = 'learn/interstitial.html'

    class Meta:
        model = models.InterstitialPage
        django_get_or_create = ['slug', 'parent']


class ListPageFactory(wagtail_factories.PageFactory):
    title = 'List page'
    live = True
    description = factory.fuzzy.FuzzyText(length=200)
    button_label = factory.fuzzy.FuzzyText(length=10)
    template = factory.fuzzy.FuzzyChoice(models.ListPage.template_choices, getter=lambda choice: choice[0])
    parent = factory.SubFactory(LandingPageFactory)
    record_read_progress = False

    class Meta:
        model = models.ListPage
        django_get_or_create = ['slug', 'parent']


class CuratedListPageFactory(wagtail_factories.PageFactory):
    title = 'Curated List Page'
    live = True
    heading = factory.fuzzy.FuzzyText(length=200)
    template = factory.fuzzy.FuzzyChoice(models.CuratedListPage.template_choices, getter=lambda choice: choice[0])
    parent = factory.SubFactory(ListPageFactory)

    class Meta:
        model = models.CuratedListPage
        django_get_or_create = ['slug', 'parent']


class TopicPageFactory(wagtail_factories.PageFactory):
    title = 'Topic page'
    live = True
    parent = factory.SubFactory(CuratedListPageFactory)

    class Meta:
        model = models.TopicPage
        django_get_or_create = ['slug', 'parent']


class LessonPlaceholderPageFactory(wagtail_factories.PageFactory):
    title = 'Placeholder'
    live = True
    parent = factory.SubFactory(TopicPageFactory)

    class Meta:
        model = models.LessonPlaceholderPage
        django_get_or_create = ['slug', 'parent']


class DetailPageFactory(wagtail_factories.PageFactory):
    title = 'Detail page'
    live = True
    body = factory.fuzzy.FuzzyText(length=200)
    template = factory.fuzzy.FuzzyChoice(models.DetailPage.template_choices, getter=lambda choice: choice[0])
    parent = factory.SubFactory(TopicPageFactory)

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']


class TourFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=90)
    body = factory.fuzzy.FuzzyText(length=200)

    class Meta:
        model = models.Tour


class SimpleVideoBlockFactory(wagtail_factories.StructBlockFactory):
    video = None

    class Meta:
        model = blocks.SimpleVideoBlock


class CaseStudyFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('word')
    summary_context = factory.Faker('word')
    lead_title = factory.fuzzy.FuzzyText(length=200)

    # Not bootstrapped:
    # body is a streamfield
    # hs_code_tags and country_code_tags use ClusterTaggableManager

    class Meta:
        model = models.CaseStudy
