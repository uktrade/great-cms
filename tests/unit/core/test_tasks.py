import datetime
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.tasks import (
    delete_inactive_admin_users_after_sixty_days,
    enact_page_schedule,
    update_geoip_data,
)
from tests.unit.core.factories import (
    MicrositeFactory,
    MicrositePageFactory,
    SuperUserFactory,
)


@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.retrieve_file')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.decompress')
def test_update_geoip_data_success(mock_decompress, mock_retrieve_file):
    update_geoip_data()

    assert mock_decompress.call_count == 2

    assert mock_retrieve_file.call_count == 2

    assert mock_retrieve_file.call_args_list == [
        mock.call(
            edition_id='GeoLite2-City',
        ),
        mock.call(
            edition_id='GeoLite2-Country',
        ),
    ]


@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.retrieve_file')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.decompress')
def test_update_geoip_data_failure(mock_decompress, mock_retrieve_file):
    mock_decompress.side_effect = ValueError()

    with pytest.raises(ValueError):
        update_geoip_data()


@pytest.mark.django_db
def test_enact_page_scheduled(rf, user, domestic_homepage):
    request = rf.get('/')
    request.user = user
    now = datetime.datetime.now()

    microsite = MicrositeFactory(
        title='Microsite',
        parent=domestic_homepage,
    )

    microsite_page_with_expire_date = MicrositePageFactory(
        slug='microsite-page-with-expire-date',
        title='Test',
        page_title='Test',
        parent=microsite,
        expire_at=now,
    )

    assert microsite_page_with_expire_date.live is True

    enact_page_schedule()
    microsite_page_with_expire_date.refresh_from_db()

    assert microsite_page_with_expire_date.live is False


@pytest.mark.django_db
def test_delete_users_after_sixty_days():
    settings.APP_ENVIRONMENT = 'local'
    two_days_ago = timezone.now() - datetime.timedelta(days=2)
    sixty_one_days_ago = timezone.now() - datetime.timedelta(days=61)

    # Create SSO user (SSO users will not be deleted, even if inactive)
    SuperUserFactory(date_joined=sixty_one_days_ago, last_login=None, password='!abc123')

    # Create users - active
    SuperUserFactory(date_joined=two_days_ago, last_login=None, is_superuser=False)
    SuperUserFactory(date_joined=two_days_ago, last_login=None)
    SuperUserFactory(date_joined=two_days_ago, last_login=two_days_ago)
    SuperUserFactory(date_joined=sixty_one_days_ago, last_login=two_days_ago)
    # Create users - inactive
    SuperUserFactory(date_joined=sixty_one_days_ago, last_login=None)
    SuperUserFactory(date_joined=sixty_one_days_ago, last_login=sixty_one_days_ago)

    user = get_user_model()
    users = user.objects.all()

    assert users.count() == 7
    delete_inactive_admin_users_after_sixty_days()
    assert users.count() == 5


@pytest.mark.django_db
def test_delete_users_raise_error_in_production():
    settings.APP_ENVIRONMENT = 'production'
    with pytest.raises(Exception, match='This task cannot be run on the current environment'):
        delete_inactive_admin_users_after_sixty_days()
