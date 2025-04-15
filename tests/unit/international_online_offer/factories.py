import factory
import factory.fuzzy

from international_online_offer.models import TradeAssociation, UserData, TriageData
from international_online_offer.core import intents, regions, spends, hirings


class TradeAssociationFactory(factory.django.DjangoModelFactory):
    trade_association_id = factory.fuzzy.FuzzyText(length=255)
    sector_grouping = factory.fuzzy.FuzzyText(length=255)
    association_name = factory.fuzzy.FuzzyText(length=255)
    website_link = factory.fuzzy.FuzzyText(length=255)
    sector = factory.fuzzy.FuzzyText(length=255)
    brief_description = factory.fuzzy.FuzzyText(length=255)
    link_valid = False

    class Meta:
        model = TradeAssociation


class UserDataFactory(factory.django.DjangoModelFactory):
    hashed_uuid = factory.fuzzy.FuzzyText(length=255)
    company_name = factory.fuzzy.FuzzyText(length=255)
    company_location = factory.fuzzy.FuzzyText(length=255)
    duns_number = factory.fuzzy.FuzzyText(length=255)
    address_line_1 = factory.fuzzy.FuzzyText(length=255)
    address_line_2 = factory.fuzzy.FuzzyText(length=255)
    town = factory.fuzzy.FuzzyText(length=255)
    county = factory.fuzzy.FuzzyText(length=255)
    postcode = factory.fuzzy.FuzzyText(length=255)
    full_name = factory.fuzzy.FuzzyText(length=255)
    role = factory.fuzzy.FuzzyText(length=255)
    email = factory.fuzzy.FuzzyText(length=255)
    telephone_number = factory.fuzzy.FuzzyText(length=255)
    agree_terms = False
    agree_info_email = False
    landing_timeframe = factory.fuzzy.FuzzyText(length=255)
    company_website = factory.fuzzy.FuzzyText(length=255)
    reminder_email_sent = None

    class Meta:
        model = UserData


class TriageDataFactory(factory.django.DjangoModelFactory):
    hashed_uuid = factory.fuzzy.FuzzyText(length=255)
    sector = 'Food and drink'
    sector_sub = 'Bakery products'
    sector_sub_sub = None
    sector_id = 'SL0223'
    intent = [intents.RESEARCH_DEVELOP_AND_COLLABORATE]
    intent_other = ''
    location = regions.WALES
    location_city = ('SWANSEA',)
    hiring = hirings.ELEVEN_TO_TWENTY
    spend = spends.LESS_THAN_FIVE_HUNDRED_THOUSAND
    spend_other = None
    is_high_value = False
    location_none = False

    class Meta:
        model = TriageData
