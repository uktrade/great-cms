from unittest import mock

import pytest

from core.models import AbstractObjectHash
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
    detail_page = factories.DetailPageFactory(parent=list_page,)

    client.get(detail_page.url)

    # then the progress is saved
    read_hit = detail_page.page_views.get()
    assert read_hit.sso_id == str(user.pk)
    assert read_hit.list_page == list_page


@pytest.mark.django_db
def test_detal_page_cannot_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    detail_page = factories.DetailPageFactory(parent=list_page)

    client.get(detail_page.url)

    # then the progress is saved
    assert detail_page.page_views.count() == 0


@pytest.mark.django_db
def test_detail_page_anon_user_not_marked_as_read(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    list_page = factories.ListPageFactory(parent=domestic_homepage)
    detail_page = factories.DetailPageFactory(parent=list_page)

    client.get(detail_page.url)

    # then the progress is unaffected
    assert detail_page.page_views.count() == 0
