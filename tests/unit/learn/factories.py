import factory

from learn import rules
from tests.unit.core import factories as core_factories


from wagtail_personalisation import models


class SegmentFactory(factory.DjangoModelFactory):
    name = factory.Faker('word')
    status = models.Segment.STATUS_ENABLED

    class Meta:
        model = models.Segment


class MatchProductQuerystringFactory(factory.django.DjangoModelFactory):
    segment = factory.SubFactory(SegmentFactory)
    product = factory.SubFactory(core_factories.ProductFactory)

    class Meta:
        model = rules.MatchProductQuerystring


class MatchCountryQuerystringFactory(factory.django.DjangoModelFactory):
    segment = factory.SubFactory(SegmentFactory)
    country = factory.SubFactory(core_factories.CountryFactory)

    class Meta:
        model = rules.MatchCountryQuerystring
