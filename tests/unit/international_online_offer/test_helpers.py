from unittest import mock

import pytest
from directory_forms_api_client import actions

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import filter_tags, helpers, regions


def test_find_articles_based_on_tags():
    class MockArticle:
        def __init__(self, specific):
            self.specific = specific

    class MockSpecific:
        def __init__(self, tags):
            self.tags = tags

    class MockTag:
        def __init__(self, name):
            self.name = name

    tag = MockTag('tag1')
    tag2 = MockTag('tag2')
    tag3 = MockTag(filter_tags.SUPPORT_AND_INCENTIVES)

    specific = MockSpecific([tag, tag2])
    specific2 = MockSpecific([tag3])
    specific3 = MockSpecific([tag])

    article = MockArticle(specific)
    article2 = MockArticle(specific)
    article3 = MockArticle(specific2)
    article4 = MockArticle(specific3)

    articles = [article, article2, article3, article4]

    assert len(helpers.find_get_to_know_market_articles(articles, 'tag1', ['tag2'])) == 3
    assert len(helpers.find_get_support_and_incentives_articles(articles)) == 1
    assert helpers.find_get_to_know_market_articles([], '', []) == []
    assert helpers.find_get_support_and_incentives_articles([]) == []
    assert helpers.find_trade_shows_for_sector([], 'tag1') == []
    assert len(helpers.find_trade_shows_for_sector(articles, 'tag1')) == 1
    assert helpers.get_trade_page([]) is None
    assert helpers.get_trade_page(articles) is not None


def test_get_trade_assoication_sectors_from_sector():
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.AEROSPACE) == []
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.FOOD_AND_DRINK) == [
        'Food and Drink'
    ]
    assert helpers.get_trade_assoication_sectors_from_sector(directory_constants_sectors.CONSUMER_AND_RETAIL) == [
        'Retail'
    ]


def test_concat_filters():
    assert helpers.concat_filters('test', ['test']) == ['test', 'test']


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
    assert helpers.get_salary_region_from_region(regions.EASTERN) == 'East'
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
    mid_query = {'median_salary__avg': 15000}
    high_query = {'median_salary__avg': 20000}
    low, mid, high = helpers.get_salary_data(low_query, mid_query, high_query)
    assert low == 10000
    assert mid == 15000
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
