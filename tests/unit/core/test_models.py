from unittest import mock

import pytest
from wagtail.tests.utils import WagtailPageTests

from core.models import AbstractObjectHash, LandingPage
from core.models import ListPage, CuratedListPage, InterstitialPage, DetailPage
from exportplan.models import ExportPlanDashboardPage
from domestic.models import DomesticHomePage, DomesticDashboard
from tests.unit.core import factories


def test_object_hash():
    mocked_file = mock.Mock()
    mocked_file.read.return_value = b'foo'
    hash = AbstractObjectHash.generate_content_hash(mocked_file)
    assert hash == 'acbd18db4cc2f85cedef654fccc4a4d8'


@pytest.mark.django_db
def test_detail_page_can_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    detail_page = factories.DetailPageFactory(parent=curated_list_page)

    client.get(detail_page.url)

    # then the progress is saved
    read_hit = detail_page.page_views.get()
    assert read_hit.sso_id == str(user.pk)
    assert read_hit.list_page == list_page


@pytest.mark.django_db
def test_detail_page_cannot_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    detail_page = factories.DetailPageFactory(parent=curated_list_page)

    client.get(detail_page.url)

    # then the progress is saved
    assert detail_page.page_views.count() == 0


@pytest.mark.django_db
def test_detail_page_anon_user_not_marked_as_read(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    list_page = factories.CuratedListPageFactory(parent=domestic_homepage)
    detail_page = factories.DetailPageFactory(parent=list_page)

    client.get(detail_page.url)

    # then the progress is unaffected
    assert detail_page.page_views.count() == 0


class LandingPageTests(WagtailPageTests):

    def test_can_be_created_under_homepage(self):
        self.assertAllowedParentPageTypes(LandingPage, {DomesticHomePage})

    def test_can_be_created_under_landing_page(self):
        self.assertAllowedSubpageTypes(
            LandingPage, {ListPage, InterstitialPage, ExportPlanDashboardPage, DomesticDashboard}
        )


class ListPageTests(WagtailPageTests):

    def test_can_be_created_under_landing_page(self):
        self.assertAllowedParentPageTypes(ListPage, {LandingPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(ListPage, {CuratedListPage})


class CuratedListPageTests(WagtailPageTests):

    def test_can_be_created_under_list_page(self):
        self.assertAllowedParentPageTypes(CuratedListPage, {ListPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(CuratedListPage, {DetailPage})


class DetailPageTests(WagtailPageTests):

    def test_can_be_created_under_curated_list_page(self):
        self.assertAllowedParentPageTypes(DetailPage, {CuratedListPage})
