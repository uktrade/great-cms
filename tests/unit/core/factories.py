import factory
import wagtail_factories
import wagtail_personalisation.models

from core import models, rules


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('word')

    class Meta:
        model = models.Product


class CountryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('word')

    class Meta:
        model = models.Country


class PersonalisedPageFactory(wagtail_factories.PageFactory):

    title = 'personalised page'
    live = True

    class Meta:
        model = models.PersonalisedPage
        django_get_or_create = ['slug', 'parent']


class SegmentFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    status = wagtail_personalisation.models.Segment.STATUS_ENABLED

    class Meta:
        model = wagtail_personalisation.models.Segment


class MatchProductQuerystringFactory(factory.django.DjangoModelFactory):
    segment = factory.SubFactory(SegmentFactory)
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = rules.MatchProductQuerystring


class MatchCountryQuerystringFactory(factory.django.DjangoModelFactory):
    segment = factory.SubFactory(SegmentFactory)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = rules.MatchCountryQuerystring


class MatchFirstCountryOfInterestFactory(factory.django.DjangoModelFactory):
    segment = factory.SubFactory(SegmentFactory)
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = rules.MatchFirstCountryOfInterestRule
