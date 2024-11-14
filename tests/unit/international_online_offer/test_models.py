from unittest import mock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.utils.text import slugify
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTests

from core.tests.helpers import create_response
from international.forms import InternationalHCSATForm
from international.models import GreatInternationalHomePage
from international_online_offer.core.hirings import TWENTY_ONE_PLUS
from international_online_offer.core.intents import SET_UP_A_NEW_DISTRIBUTION_CENTRE
from international_online_offer.core.landing_timeframes import UNDER_SIX_MONTHS
from international_online_offer.core.spends import ONE_MILLION_TO_TWO_MILLION
from international_online_offer.models import (
    EYBArticlePage,
    EYBArticlePageTag,
    EYBArticlesPage,
    EYBArticleTag,
    EYBGuidePage,
    EYBIndexPage,
    EYBTradeShowPageTag,
    EYBTradeShowsPage,
    IOOTradeShowPage,
    TriageData,
    UserData,
    get_triage_data_for_user,
    get_user_data_for_user,
)


class EYBIndexPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            EYBIndexPage,
            {
                GreatInternationalHomePage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            EYBIndexPage,
            {
                EYBGuidePage,
            },
        )


class EYBGuidePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            EYBGuidePage,
            {
                EYBIndexPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            EYBGuidePage,
            {EYBArticlePage, EYBTradeShowsPage, EYBArticlesPage},
        )


class EYBTradeShowsPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            EYBTradeShowsPage,
            {
                EYBGuidePage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            EYBTradeShowsPage,
            {IOOTradeShowPage},
        )


class EYBTradeShowPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOTradeShowPage,
            {
                EYBTradeShowsPage,
            },
        )


@pytest.mark.parametrize(
    'user_sector, sector_tag, expected_len_articles',
    (
        ('Automotive', 'automotive', 1),
        ('Agriculture, horticulture, fisheries and pets', 'Agriculture horticulture fisheries and pets', 1),
        ('Food and drink', 'FOOD AND DRINK', 1),
        ('Financial and professional services', 'Financial and Professional Services', 1),
    ),
)
@mock.patch('international_online_offer.services.get_bci_data_by_dbt_sector', return_value=[])
@pytest.mark.django_db
def test_eyb_guide_page_content(rf, user, domestic_site, user_sector, sector_tag, expected_len_articles):

    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={
            'sector': user_sector,
            'intent': [SET_UP_A_NEW_DISTRIBUTION_CENTRE],
            'location_none': True,
            'spend': [ONE_MILLION_TO_TWO_MILLION],
            'hiring': [TWENTY_ONE_PLUS],
        },
    )

    UserData.objects.update_or_create(
        hashed_uuid='123',
        defaults={
            'full_name': 'Joe Bloggs',
            'company_location': 'FJ',
            'company_name': 'DBT Co.',
            'address_line_1': '123 high street',
            'town': 'The town',
            'role': 'Developer',
            'telephone_number': '07912345678',
            'landing_timeframe': [UNDER_SIX_MONTHS],
        },
    )

    root = Page.get_first_root_node()

    article_page = EYBArticlePage(
        article_title='test123',
        title='test123',
        slug='test123',
    )

    guide_page = EYBGuidePage(title='Guide')
    root.add_child(instance=guide_page)
    root.add_child(instance=article_page)

    # tag with users sector
    sector_tag = EYBArticleTag(name=sector_tag, slug=slugify(sector_tag))
    sector_tag.save()
    page_tag = EYBArticlePageTag(tag=sector_tag, content_object=article_page)
    page_tag.save()

    # tag with intent
    intent_tag = EYBArticleTag(name=SET_UP_A_NEW_DISTRIBUTION_CENTRE, slug=slugify(SET_UP_A_NEW_DISTRIBUTION_CENTRE))
    intent_tag.save()
    page_tag = EYBArticlePageTag(tag=intent_tag, content_object=article_page)
    page_tag.save()

    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    request.session = {}
    response = guide_page.serve(request)
    context = response.context_data
    assert context['complete_contact_form_link_text'] == 'Sign up'
    assert context['complete_contact_form_link'] == 'international_online_offer:signup'
    assert len(context['get_to_know_market_articles']) == expected_len_articles
    assert len(context['finance_and_support_articles']) == 0
    assert context['trade_shows_page'] is None


@pytest.mark.parametrize(
    'user_sector, tradeshow_tag, expected_len_tradeshows',
    (
        ('Automotive', 'automotive', 1),
        ('Agriculture, horticulture, fisheries and pets', 'Agriculture horticulture fisheries and pets', 1),
        ('Food and drink', 'FOOD AND DRINK', 1),
        ('Financial and professional services', 'Financial and Professional Services', 1),
    ),
)
@pytest.mark.django_db
def test_eyb_trade_page_content(rf, user, domestic_site, user_sector, tradeshow_tag, expected_len_tradeshows):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': user_sector},
    )

    root = Page.get_first_root_node()

    eyb_tradeshow_page = EYBTradeShowsPage(
        title='test',
        slug='test',
    )

    ioo_tradeshow_page = IOOTradeShowPage(
        tradeshow_title='test123',
        title='test123',
        slug='test123',
    )

    root.add_child(instance=eyb_tradeshow_page)
    root.add_child(instance=ioo_tradeshow_page)

    eyb_article_tag = EYBArticleTag(name=tradeshow_tag, slug=slugify(tradeshow_tag))
    eyb_article_tag.save()
    tradeshow_tag = EYBTradeShowPageTag(tag=eyb_article_tag, content_object=ioo_tradeshow_page)
    tradeshow_tag.save()

    request = rf.get(eyb_tradeshow_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    request.session = {}
    context = eyb_tradeshow_page.get_context(request)
    assert len(context['all_tradeshows']) == expected_len_tradeshows


@pytest.mark.django_db
def test_eyb_guide_get_triage_data_none(rf, user):
    guide_page = EYBTradeShowsPage(title='Trade')
    request = rf.get(guide_page.url)
    data = get_triage_data_for_user(request)
    assert data is None
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    data = get_triage_data_for_user(request)
    assert data is None


@pytest.mark.django_db
def test_eyb_guide_get_triage_data(rf, user, get_response):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    guide_page = EYBGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    middleware = SessionMiddleware(get_response)
    middleware.process_request(request)
    request.session.save()
    triage_data = get_triage_data_for_user(request)
    assert triage_data is not None
    assert triage_data.sector == 'sector'


@pytest.mark.django_db
def test_eyb_guide_get_user_from_db(rf, user):
    UserData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'full_name': 'Joe', 'company_name': 'DBT'},
    )
    guide_page = EYBGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    user_data = get_user_data_for_user(request)
    assert user_data is not None
    assert user_data.full_name == 'Joe'
    assert user_data.company_name == 'DBT'


class EYBArticlePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            EYBArticlePage,
            {EYBGuidePage, EYBArticlesPage},
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            EYBArticlePage,
            {},
        )


class EYBArticlesPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            EYBArticlesPage,
            {
                EYBGuidePage,
                EYBArticlesPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            EYBArticlesPage,
            {EYBArticlesPage, EYBArticlePage},
        )


@mock.patch('directory_api_client.api_client.dataservices.get_eyb_salary_data', return_value=create_response({}))
@mock.patch(
    'directory_api_client.api_client.dataservices.get_eyb_commercial_rent_data', return_value=create_response({})
)
@pytest.mark.django_db
def test_article_page_context(mock_get_median_salaries, mock_get_rent_data, user):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'Food and drink', 'location': 'WALES'},
    )

    page = EYBArticlePage(
        title='Test EYB Article Page',
        article_title='Test Article',
    )

    request = RequestFactory().get('/any/')
    user.hashed_uuid = '123'
    request.user = user
    request.session = {}

    output = page.get_context(request=request)
    assert output['professions_by_sector']['sector'] == 'Food and drink'


@pytest.mark.django_db
def test_eyb_hcsat():
    pages = [
        EYBArticlePage(
            title='Test EYB Article Page',
            article_title='Test Article',
        ),
        EYBGuidePage(title='Guide'),
        EYBTradeShowsPage(title='Trade'),
    ]

    for page in pages:
        assert page.is_international_hcsat is True
        assert page.hcsat_service_name == 'eyb'
        assert type(page.get_csat_form()) == InternationalHCSATForm
        assert (
            page.get_service_csat_heading(page.hcsat_service_name)
            == 'Overall, how would you rate your experience with the\n         Expand your business service today?'
        )
