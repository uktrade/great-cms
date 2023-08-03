import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from wagtail.test.utils import WagtailPageTests

from domestic.models import StructuralPage
from international_online_offer.core import constants
from international_online_offer.models import (
    IOOArticlePage,
    IOOGuidePage,
    IOOIndexPage,
    IOOTradePage,
    IOOTradeShowPage,
    TriageData,
    UserData,
    get_triage_data,
    get_triage_data_from_db_or_session,
)


class IOOIndexPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOIndexPage,
            {
                StructuralPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOIndexPage,
            {
                IOOGuidePage,
            },
        )


class IOOGuidePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOGuidePage,
            {
                IOOIndexPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOGuidePage,
            {IOOArticlePage, IOOTradePage},
        )


class IOOTradePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOTradePage,
            {
                IOOGuidePage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOTradePage,
            {IOOTradeShowPage},
        )


class IOOTradeShowPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOTradeShowPage,
            {
                IOOTradePage,
            },
        )


@pytest.mark.django_db
def test_ioo_guide_page_content(rf):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    context = guide_page.get_context(request)
    assert context['complete_contact_form_message'] == constants.LOW_VALUE_INVESTOR_SIGNUP_MESSAGE
    assert context['complete_contact_form_link_text'] == 'Sign up'
    assert context['complete_contact_form_link'] == 'international_online_offer:signup'
    assert context['get_to_know_market_articles'] == []
    assert context['support_and_incentives_articles'] == []
    assert context['trade_page'] is None


@pytest.mark.django_db
def test_ioo_trade_page_content(rf):
    guide_page = IOOTradePage(title='Trade')
    request = rf.get(guide_page.url)
    context = guide_page.get_context(request)
    assert context['all_tradeshows'] == []


@pytest.mark.django_db
def test_ioo_guide_get_triage_data_none(rf):
    data = get_triage_data('testId')
    assert data is None


@pytest.mark.django_db
def test_ioo_guide_get_triage_data(rf):
    TriageData.objects.update_or_create(
        hashed_uuid='testId',
        defaults={'spend': 'spend', 'spend_other': 'spend_other'},
    )
    data = get_triage_data('testId')
    assert data is not None
    assert data.hashed_uuid == 'testId'
    assert data.spend == 'spend'
    assert data.spend_other == 'spend_other'


@pytest.mark.django_db
def test_ioo_guide_get_triage_from_db_not_session(rf, user, get_response):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    middleware = SessionMiddleware(get_response)
    middleware.process_request(request)
    request.session.save()
    triage_data = get_triage_data_from_db_or_session(request)
    assert triage_data is not None
    assert triage_data.sector == 'sector'


@pytest.mark.django_db
def test_ioo_guide_get_triage_from_session_not_db(rf, get_response):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    middleware = SessionMiddleware(get_response)
    middleware.process_request(request)
    request.session.save()
    request.session['sector'] = 'sector'
    triage_data_session = get_triage_data_from_db_or_session(request)
    assert triage_data_session is not None
    assert triage_data_session.sector == 'sector'


@pytest.mark.django_db
def test_ioo_guide_get_user_from_db(rf, user):
    UserData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'full_name': 'Joe', 'company_name': 'DBT'},
    )
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    user_data = UserData.objects.filter(hashed_uuid=request.user.hashed_uuid).first()
    assert user_data is not None
    assert user_data.full_name == 'Joe'
    assert user_data.company_name == 'DBT'


class IOOArticlePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOArticlePage,
            {
                IOOGuidePage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOArticlePage,
            {},
        )


@pytest.mark.django_db
def test_article_page_context(client, user):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'FOOD_AND_DRINK', 'location': 'WALES'},
    )

    page = IOOArticlePage(
        title='Test IOO Article Page',
        article_title='Test Article',
    )

    request = RequestFactory().get('/any/')
    user.hashed_uuid = '123'
    request.user = user

    output = page.get_context(request=request)
    assert output['professions_by_sector']['sector'] == 'FOOD_AND_DRINK'
