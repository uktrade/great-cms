import factory
import factory.fuzzy
import wagtail_factories
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from core import blocks, constants, models
from core.models import Microsite, MicrositePage
from domestic import models as domestic_models
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
    title_id = factory.LazyAttribute(lambda obj: slugify(obj.title))
    hide_title = False

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


class TopicLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = domestic_models.TopicLandingPage


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


class StructurePageFactory(wagtail_factories.PageFactory):
    title = 'Structure'
    live = True

    class Meta:
        model = domestic_models.StructuralPage
        django_get_or_create = ['slug', 'parent']


class DetailPageFactory(wagtail_factories.PageFactory):
    title = 'Detail page'
    live = True
    body = wagtail_factories.StreamFieldFactory({'body': factory.fuzzy.FuzzyText(length=90)})
    template = factory.fuzzy.FuzzyChoice(models.DetailPage.template_choices, getter=lambda choice: choice[0])
    parent = factory.SubFactory(TopicPageFactory)

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']


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


class IndustryTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IndustryTag

    name = factory.fuzzy.FuzzyText(length=10)
    icon = factory.SubFactory(wagtail_factories.ImageFactory)


class MicrositePageFactory(wagtail_factories.PageFactory):
    last_published_at = timezone.now()

    class Meta:
        model = MicrositePage


class MicrositeFactory(wagtail_factories.PageFactory):
    last_published_at = timezone.now()

    class Meta:
        model = Microsite


class BlockFactory:
    def __init__(self, block_type):
        self.block_type = block_type
        self.value = []


class SuperUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('email')
    password = factory.LazyFunction(lambda: make_password('abc123'))
    is_staff = True
    is_superuser = True


class HCSATFactory(factory.django.DjangoModelFactory):

    URL = factory.fuzzy.FuzzyText(length=100)
    user_journey = factory.fuzzy.FuzzyChoice(constants.USER_JOURNEY_CHOICES, getter=lambda choice: choice[0])
    satisfaction_rating = factory.fuzzy.FuzzyChoice(constants.SATISFACTION_CHOICES, getter=lambda choice: choice[0])
    experienced_issues = [factory.fuzzy.FuzzyChoice(constants.EXPERIENCE_CHOICES, getter=lambda choice: choice[0])]
    other_detail = factory.fuzzy.FuzzyText(length=255)
    service_improvements_feedback = factory.fuzzy.FuzzyText(length=255)
    likelihood_of_return = factory.fuzzy.FuzzyChoice(constants.LIKELIHOOD_CHOICES, getter=lambda choice: choice[0])
    service_name = factory.fuzzy.FuzzyChoice(['export_academy', 'find_a_buyer', 'eyb'])
    service_specific_feedback = ['HELP_US_SET_UP_IN_THE_UK', 'PUT_US_IN_TOUCH_WITH_EXPERTS']
    service_specific_feedback_other = factory.fuzzy.FuzzyText(length=255)

    class Meta:
        model = models.HCSAT
