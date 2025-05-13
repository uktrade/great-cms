from random import randint
from secrets import token_urlsafe

import factory
import wagtail_factories
from faker import Faker

from domestic_growth.choices import (
    EXISTING_BUSINESS_TURNOVER_CHOICES,
    EXISTING_BUSINESS_WHEN_SET_UP_CHOICES,
)
from domestic_growth.models import (
    DomesticGrowthChildGuidePage,
    DomesticGrowthDynamicChildGuidePage,
    DomesticGrowthGuidePage,
    DomesticGrowthHomePage,
    ExistingBusinessGuideEmailRecipient,
    ExistingBusinessTriage,
    StartingABusinessGuideEmailRecipient,
    StartingABusinessTriage,
)


class DomesticGrowthHomePageFactory(wagtail_factories.PageFactory):
    title = 'homepage'
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticGrowthHomePage


class DomesticGrowthGuidePageFactory(wagtail_factories.PageFactory):
    title = 'guidepage'
    live = True
    slug = 'guidepage'

    class Meta:
        model = DomesticGrowthGuidePage


class DomesticGrowthChildGuidePageFactory(wagtail_factories.PageFactory):
    title = 'child-guidepage'
    live = True
    slug = 'child-guidepage'

    class Meta:
        model = DomesticGrowthChildGuidePage


class DomesticGrowthDynamicChildGuidePageFactory(wagtail_factories.PageFactory):
    title = 'dynamic-child-guidepage'
    live = True
    slug = 'dynamic-child-guidepage'

    class Meta:
        model = DomesticGrowthDynamicChildGuidePage


class DomesticGrowthExistingBusinessTriageFactory(factory.django.DjangoModelFactory):
    triage_uuid = factory.Faker('uuid4')
    # format of sector_id is SL0001 through to SL0351, i.e. includes padding zeros
    sector_id = f'SL{str(randint(1, 351) + 10000)[1:]}'
    cant_find_sector = False
    postcode = Faker().postcode()
    when_set_up = factory.fuzzy.FuzzyChoice(EXISTING_BUSINESS_WHEN_SET_UP_CHOICES)
    turnover = factory.fuzzy.FuzzyChoice(EXISTING_BUSINESS_TURNOVER_CHOICES)
    currently_export = factory.fuzzy.FuzzyChoice([True, False])

    class Meta:
        model = ExistingBusinessTriage


class DomesticGrowthExistingBusinessGuideEmailRecipientFactory(factory.django.DjangoModelFactory):
    email = Faker().email()
    triage = factory.SubFactory(DomesticGrowthExistingBusinessTriageFactory)
    url_token = token_urlsafe(128)

    class Meta:
        model = ExistingBusinessGuideEmailRecipient


class DomesticGrowthStartingABusinessTriageFactory(factory.django.DjangoModelFactory):
    triage_uuid = factory.Faker('uuid4')
    # format of sector_id is SL0001 through to SL0351, i.e. includes padding zeros
    sector_id = f'SL{str(randint(1, 351) + 10000)[1:]}'
    dont_know_sector = False
    postcode = Faker().postcode()

    class Meta:
        model = StartingABusinessTriage


class DomesticGrowthStartingABusinessGuideEmailRecipientFactory(factory.django.DjangoModelFactory):
    email = Faker().email()
    triage = factory.SubFactory(DomesticGrowthStartingABusinessTriageFactory)
    url_token = token_urlsafe(128)

    class Meta:
        model = StartingABusinessGuideEmailRecipient
