import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from wagtail.test.utils import WagtailPageTests

from domestic.models import StructuralPage
from international.models import GreatInternationalHomePage
from international_online_offer.models import (
    EYBArticlePage,
    EYBArticlesPage,
    EYBGuidePage,
    EYBIndexPage,
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
                StructuralPage,
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


@pytest.mark.django_db
def test_eyb_guide_page_content(rf, user):
    guide_page = EYBGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    context = guide_page.get_context(request)
    assert context['complete_contact_form_link_text'] == 'Sign up'
    assert context['complete_contact_form_link'] == 'international_online_offer:signup'
    assert len(context['get_to_know_market_articles']) == 0
    assert len(context['finance_and_support_articles']) == 0
    assert context['trade_shows_page'] is None


@pytest.mark.django_db
def test_eyb_trade_page_content(rf):
    guide_page = EYBTradeShowsPage(title='Trade')
    request = rf.get(guide_page.url)
    context = guide_page.get_context(request)
    assert context['all_tradeshows'] == []


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


@pytest.mark.django_db
def test_article_page_context(client, user):
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

    output = page.get_context(request=request)
    assert output['professions_by_sector']['sector'] == 'Food and drink'
