import factory
import factory.fuzzy

from international_online_offer.models import TradeAssociation, UserData


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

    class Meta:
        model = UserData
