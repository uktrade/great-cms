import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from wagtail.tests.utils import WagtailPageTests

from domestic.models import StructuralPage
from international_online_offer.models import (
    IOOArticlePage,
    IOOGuidePage,
    IOOIndexPage,
    TriageData,
    UserData,
    get_triage_data,
    get_triage_data_from_db_or_session,
    get_user_data,
    get_user_data_from_db_or_session,
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
            {IOOArticlePage},
        )


@pytest.mark.django_db
def test_ioo_guide_page_content(rf):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    context = guide_page.get_context(request)
    assert context['complete_contact_form_message'] == IOOGuidePage.LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
    assert context['complete_contact_form_link_text'] == 'Complete form'
    assert context['complete_contact_form_link'] == 'international_online_offer:signup'
    assert context['get_to_know_market_articles'] == []
    assert context['support_and_incentives_articles'] == []
    assert context['opportunities_articles'] == []


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
def test_ioo_guide_get_user_data_none(rf):
    data = get_user_data('testId')
    assert data is None


@pytest.mark.django_db
def test_ioo_guide_get_user_data(rf):
    UserData.objects.update_or_create(
        hashed_uuid='testId',
        defaults={'full_name': 'Joe', 'company_name': 'DBT'},
    )
    data = get_user_data('testId')
    assert data is not None
    assert data.hashed_uuid == 'testId'
    assert data.full_name == 'Joe'
    assert data.company_name == 'DBT'


@pytest.mark.django_db
def test_ioo_guide_get_triage_from_db_not_session(rf, user):
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    triage_data = get_triage_data_from_db_or_session(request)
    assert triage_data is not None
    assert triage_data.sector == 'sector'


@pytest.mark.django_db
def test_ioo_guide_get_triage_from_session_not_db(rf):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    request.session['sector'] = 'sector'
    triage_data_session = get_triage_data_from_db_or_session(request)
    assert triage_data_session is not None
    assert triage_data_session.sector == 'sector'


@pytest.mark.django_db
def test_ioo_guide_get_user_from_session_not_db(rf):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    request.session['full_name'] = 'full_name'
    user_data_session = get_user_data_from_db_or_session(request)
    assert user_data_session is not None
    assert user_data_session.full_name == 'full_name'


@pytest.mark.django_db
def test_ioo_guide_get_user_from_db_not_session(rf, user):
    UserData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'full_name': 'Joe', 'company_name': 'DBT'},
    )
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    request.user = user
    request.user.hashed_uuid = '123'
    user_data = get_user_data_from_db_or_session(request)
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
