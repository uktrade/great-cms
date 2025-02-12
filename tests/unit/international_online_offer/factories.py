import factory
import factory.fuzzy

from international_online_offer.models import TradeAssociation


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
