from unittest import mock

import pytest
from directory_forms_api_client import actions

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import (
    helpers,
    hirings,
    intents,
    regions,
    sectors,
    spends,
)
from international_online_offer.models import TriageData


def test_find_articles_based_on_tags():
    class MockArticle:
        def __init__(self, tags):
            self.tags = tags

    class MockTag:
        def __init__(self, name):
            self.name = name

    tag = MockTag(sectors.TECHNOLOGY_AND_SMART_CITIES)
    tag2 = MockTag(sectors.CREATIVE_INDUSTRIES)
    tag3 = MockTag(intents.SET_UP_A_NEW_DISTRIBUTION_CENTRE)
    tag4 = MockTag(intents.SET_UP_NEW_PREMISES)

    article_tech = MockArticle([tag])
    article_creative = MockArticle([tag2])
    article_tech_and_dist_centre = MockArticle([tag, tag3])
    article_tech_and_premises = MockArticle([tag, tag4])

    articles = [article_tech, article_creative, article_tech_and_dist_centre, article_tech_and_premises]

    assert len(helpers.filter_articles_sector_only(articles)) == 2
    assert len(helpers.filter_intent_articles_specific_to_sector(articles, sectors.TECHNOLOGY_AND_SMART_CITIES)) == 3
    assert helpers.filter_articles_sector_only([]) == []
    assert helpers.filter_intent_articles_specific_to_sector([], sectors.TECHNOLOGY_AND_SMART_CITIES) == []


def test_can_show_salary_rent_component():
    class MockTag:
        def __init__(self, name):
            self.name = name

    tag = MockTag(sectors.TECHNOLOGY_AND_SMART_CITIES)
    tag2 = MockTag(intents.SET_UP_A_NEW_DISTRIBUTION_CENTRE)
    tag3 = MockTag(intents.SET_UP_NEW_PREMISES)
    tag4 = MockTag(intents.FIND_PEOPLE_WITH_SPECIALIST_SKILLS)

    assert helpers.can_show_salary_component([tag]) is False
    assert helpers.can_show_salary_component([tag, tag4]) is True
    assert helpers.can_show_rent_component([tag]) is False
    assert helpers.can_show_rent_component([tag, tag2]) is True
    assert helpers.can_show_rent_component([tag, tag3]) is True


def test_get_trade_assoication_sectors_from_sector():
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.AEROSPACE) == []
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.FOOD_AND_DRINK) == [
        'Food and Drink'
    ]
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.CONSUMER_AND_RETAIL) == [
        'Retail'
    ]


@mock.patch.object(actions, 'GovNotifyEmailAction')
def test_send_eyb_welcome_notification(mock_action_class, settings):
    helpers.send_welcome_notification(email='jim@example.com', form_url='foo')

    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address='jim@example.com',
        form_url='foo',
    )
    assert mock_action_class().save.call_count == 1


@pytest.mark.django_db
def test_get_salary_region_from_region():
    assert helpers.get_salary_region_from_region(regions.EAST_OF_ENGLAND) == 'East'
    assert helpers.get_salary_region_from_region(regions.WALES) == 'Wales'


@pytest.mark.django_db
def test_is_authenticated():
    assert helpers.is_authenticated(None) is False
    user_not_logged_in = type(
        'obj',
        (object,),
        {'is_authenticated': False},
    )
    request = type(
        'obj',
        (object,),
        {'user': user_not_logged_in},
    )
    assert helpers.is_authenticated(request) is False
    user_logged_in = type(
        'obj',
        (object,),
        {'is_authenticated': True},
    )
    request.user = user_logged_in
    assert helpers.is_authenticated(request) is True


@pytest.mark.django_db
def test_get_salary_data():
    low_query = {'median_salary__avg': 10000}
    mid_query = {'median_salary__avg': 5000}
    high_query = {'median_salary__avg': 20000}
    low, mid, high = helpers.get_salary_data(low_query, mid_query, high_query)
    assert low == 10000
    assert mid is None
    assert high == 20000


@pytest.mark.django_db
def test_get_rent_data():
    class RentQueryResult:
        def __init__(self, gbp_per_month):
            self.gbp_per_month = gbp_per_month

    large_query = RentQueryResult(20000)
    small_query = RentQueryResult(1000)
    shopping_query = RentQueryResult(2000)
    high_steet_query = RentQueryResult(3000)
    office_query = RentQueryResult(4000)
    large, small, shopping, high_steet, office = helpers.get_rent_data(
        large_query, small_query, shopping_query, high_steet_query, office_query
    )
    assert large == 20000
    assert small == 1000
    assert shopping == 2000
    assert high_steet == 3000
    assert office == 4000


@pytest.mark.django_db
def test_get_sector_professions_by_level():
    food_drink_profession = helpers.get_sector_professions_by_level(directory_constants_sectors.FOOD_AND_DRINK)
    assert food_drink_profession['entry_level'] == 'bartenders, waiting staff and cooks'


@pytest.mark.django_db
def test_is_triage_complete():
    mock_triage_data = TriageData()
    mock_triage_data.sector = directory_constants_sectors.FOOD_AND_DRINK
    mock_triage_data.intent_other = 'TEST OTHER INTENT'
    mock_triage_data.location = regions.LONDON
    mock_triage_data.hiring = hirings.ELEVEN_TO_FIFTY
    mock_triage_data.spend = spends.FIVE_HUNDRED_THOUSAND_ONE_TO_ONE_MILLION
    assert helpers.is_triage_complete(None) is False
    assert helpers.is_triage_complete(mock_triage_data) is True
