import datetime
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from core.tasks import (
    delete_inactive_admin_users_after_sixty_days,
    enact_page_schedule,
    submit_hcsat_feedback_to_forms_api,
    update_geoip_data,
)
from tests.unit.core.factories import (
    HCSATFactory,
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


@mock.patch('directory_forms_api_client.actions.HCSatAction')
@pytest.mark.django_db
def test_submit_hcsat_feedback_to_forms_api_task(mock_hcsat_action):
    feedback_date = '2012-01-14 12:00:02'
    with freeze_time(feedback_date):
        submission_1 = HCSATFactory(created=feedback_date)
        submission_2 = HCSATFactory(created=feedback_date)

        # Run task - we are testing
        submit_hcsat_feedback_to_forms_api()
        assert mock_hcsat_action.call_count == 1
        assert mock_hcsat_action().save.call_count == 1

        expected = mock.call(
            {
                'hcsat_feedback_entries': [
                    {
                        'id': submission_1.id,
                        'feedback_submission_date': feedback_date,
                        'url': submission_1.URL,
                        'user_journey': submission_1.user_journey,
                        'satisfaction_rating': submission_1.satisfaction_rating,
                        'experienced_issues': submission_1.experienced_issues,
                        'other_detail': submission_1.other_detail,
                        'service_improvements_feedback': submission_1.service_improvements_feedback,
                        'likelihood_of_return': submission_1.likelihood_of_return,
                        'service_name': submission_1.service_name,
                        'service_specific_feedback': submission_1.service_specific_feedback,
                        'service_specific_feedback_other': submission_1.service_specific_feedback_other,
                    },
                    {
                        'id': submission_2.id,
                        'feedback_submission_date': feedback_date,
                        'url': submission_2.URL,
                        'user_journey': submission_2.user_journey,
                        'satisfaction_rating': submission_2.satisfaction_rating,
                        'experienced_issues': submission_2.experienced_issues,
                        'other_detail': submission_2.other_detail,
                        'service_improvements_feedback': submission_2.service_improvements_feedback,
                        'likelihood_of_return': submission_2.likelihood_of_return,
                        'service_name': submission_2.service_name,
                        'service_specific_feedback': submission_2.service_specific_feedback,
                        'service_specific_feedback_other': submission_2.service_specific_feedback_other,
                    },
                ]
            }
        )

        assert mock_hcsat_action().save.call_args == expected
