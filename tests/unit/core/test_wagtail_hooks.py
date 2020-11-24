import json

from unittest import mock
from datetime import timedelta

import pytest

from boto3.exceptions import RetriesExceededError, S3UploadFailedError

from django.db.models import FileField
from django.test import override_settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from wagtail.core.rich_text import RichText

from core import wagtail_hooks
from core.wagtail_hooks import (
    register_s3_media_file_adapter,
    S3FileFieldAdapter,
    S3WagtailTransferFile,
    FileTransferError,
)
from tests.helpers import make_test_video
from tests.unit.core import factories
from tests.unit.exportplan.factories import (
    ExportPlanPseudoDashboardPageFactory,
    ExportPlanPageFactory,
)
from tests.unit.learn.factories import LessonPageFactory

LOREM_IPSUM = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
    'Verum hoc loco sumo verbis his eandem certe vim voluptatis '
    'Epicurum nosse quam ceteros. Consequentia exquirere, quoad sit '
    'id, quod volumus, effectum. Et quidem saepe quaerimus verbum '
    'Latinum par Graeco et quod idem valeat; Quam illa ardentis '
    'amores excitaret sui! Cur tandem? Nihil est enim, de quo aliter '
    'tu sentias atque ego, modo commutatis verbis ipsas res conferamus. '
)


@pytest.mark.django_db
def test_anonymous_user_required_handles_anonymous_users(rf, domestic_homepage):
    request = rf.get('/')
    request.user = AnonymousUser()

    response = wagtail_hooks.anonymous_user_required(
        page=domestic_homepage,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None


@pytest.mark.django_db
def test_anonymous_user_required_handles_authenticated_users(rf, domestic_homepage, user):
    request = rf.get('/')
    request.user = user

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    response = wagtail_hooks.anonymous_user_required(
        page=domestic_homepage,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response.status_code == 302
    assert response.url == domestic_homepage.anonymous_user_required_redirect_url


@pytest.mark.django_db
def test_anonymous_user_required_handles_public_pages(rf, exportplan_homepage):
    request = rf.get('/')
    request.user = AnonymousUser()

    response = wagtail_hooks.anonymous_user_required(
        page=exportplan_homepage,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None


@pytest.mark.django_db
def test_login_required_signup_wizard_ignores_irrelevant_pages(rf, domestic_homepage):

    request = rf.get('/')
    request.user = AnonymousUser()

    response = wagtail_hooks.login_required_signup_wizard(
        page=domestic_homepage,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None


@pytest.mark.django_db
def test_login_required_signup_wizard_handles_anonymous_users(rf, domestic_homepage):
    page = LessonPageFactory(parent=domestic_homepage)

    request = rf.get('/foo/bar/')
    request.user = AnonymousUser()
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    response = wagtail_hooks.login_required_signup_wizard(
        page=page,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response.status_code == 302
    assert response.url == '/signup/tailored-content/start/?next=/foo/bar/'


@pytest.mark.django_db
def test_login_required_signup_wizard_handles_anonymous_users_opting_out(rf, domestic_homepage, user):
    page = LessonPageFactory(parent=domestic_homepage)

    first_request = rf.get('/foo/bar/', {'show-generic-content': True})
    first_request.user = AnonymousUser()

    middleware = SessionMiddleware()
    middleware.process_request(first_request)
    first_request.session.save()

    response = wagtail_hooks.login_required_signup_wizard(
        page=page,
        request=first_request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None

    second_request = rf.get('/foo/bar/')
    second_request.user = user
    second_request.session = first_request.session
    response = wagtail_hooks.login_required_signup_wizard(
        page=page,
        request=second_request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None


@pytest.mark.django_db
def test_login_required_signup_wizard_handles_authenticated_users(rf, user, domestic_homepage):
    page = LessonPageFactory(parent=domestic_homepage)

    request = rf.get('/')
    request.user = user

    response = wagtail_hooks.login_required_signup_wizard(
        page=page,
        request=request,
        serve_args=[],
        serve_kwargs={},
    )

    assert response is None


@pytest.mark.django_db
def test_login_required_signup_wizard_exportplan_logged_in(domestic_site, user, rf):

    exportplan_page = ExportPlanPageFactory(parent=domestic_site.root_page, slug='export-plan')
    exportplan_dashboard_page = ExportPlanPseudoDashboardPageFactory(parent=exportplan_page, slug='dashboard')

    for page in [exportplan_page, exportplan_dashboard_page]:

        request = rf.get(page.url)
        request.user = user

        response = wagtail_hooks.login_required_signup_wizard(
            page=page,
            request=request,
            serve_args=[],
            serve_kwargs={},
        )

        assert response is None


@pytest.mark.django_db
def test_estimated_read_time_calculation(rf, domestic_homepage):

    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    reading_content = f'<p>{ LOREM_IPSUM * 10}</p>'

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        hero=[],
        body=[],
        objective=[
            ('paragraph', RichText(reading_content))
        ],
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=153)

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request
    )

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration == expected_duration


@pytest.mark.django_db
def test_estimated_read_time_calculation__checks_text_and_video(rf, domestic_homepage):

    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    video_for_hero = make_test_video(duration=123)
    video_for_hero.save()

    reading_content = f'<p>{ LOREM_IPSUM * 10}</p>'

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        hero=[
            ('Video', factories.SimpleVideoBlockFactory(video=video_for_hero)),
        ],
        objective=[
            ('paragraph', RichText(reading_content))
        ],
        body=[
            # For now, the body ONLY contains PersonalisedStructBlocks, which don't
            # count towards page read or view time.
            # WARNING: These is a fiddle to set up in tests, so estimate appropriate
            # time for if/when we need to.
        ],
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=155 + 123)  # reading + watching

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request
    )

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration == expected_duration


@pytest.mark.django_db
def test_estimated_read_time_calculation__checks_video(rf, domestic_homepage):

    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    video_for_hero = make_test_video(duration=123)
    video_for_hero.save()

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        hero=[
            ('Video', factories.SimpleVideoBlockFactory(video=video_for_hero)),
        ],
        objective=[],
        body=[
            # For now, the body ONLY contains PersonalisedStructBlocks, which don't
            # count towards page read or view time.
            # WARNING: These is a fiddle to set up in tests, so estimate appropriate
            # time for if/when we need to.
        ],
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=5 + 123)  # reading + watching

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request
    )

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration == expected_duration


@pytest.mark.django_db
def test_estimated_read_time_calculation__updates_only_draft_if_appropriate(
    rf, domestic_homepage
):

    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    video_for_hero = make_test_video(duration=124)
    video_for_hero.save()

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    assert detail_page.live is True

    original_live_read_duration = detail_page.estimated_read_duration
    assert original_live_read_duration is None

    # Note: for test simplicity here, we're not adding streamfield content to our
    # revision - it is enough to just notice how the readtimes for Draft vs Live
    # are appropriate updated at the expected times, based on the minimal default
    # content of a DetailPage.

    revision = detail_page.save_revision()
    assert json.loads(revision.content_json)['estimated_read_duration'] == original_live_read_duration

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request
    )

    detail_page.refresh_from_db()

    expected_duration = timedelta(seconds=4)  # NB just the read time of a skeleton DetailPage

    # show the live version is not updated yet
    assert detail_page.has_unpublished_changes is True
    assert detail_page.estimated_read_duration != expected_duration
    assert detail_page.estimated_read_duration == original_live_read_duration

    # but the draft is
    latest_rev = detail_page.get_latest_revision()
    assert revision == latest_rev
    assert json.loads(latest_rev.content_json)['estimated_read_duration'] == str(expected_duration)

    # Now publish the draft and show it updates the live, too
    latest_rev.publish()

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request
    )

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != original_live_read_duration

    # NOTE: for a reason unrelated to the point of _this_ test, the readtime
    # of the published page CAN BE calculated as slightly longer than the draft.
    # This may be in part due to the page having a very small amount of content.
    assert detail_page.estimated_read_duration == timedelta(seconds=4)


@pytest.mark.django_db
def test_estimated_read_time_calculation__forced_update_of_live(
    rf, domestic_homepage
):
    # This test is a variant of test_estimated_read_time_calculation__updates_only_draft_if_appropriate

    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    video_for_hero = make_test_video(duration=124)
    video_for_hero.save()

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    assert detail_page.live is True

    original_live_read_duration = detail_page.estimated_read_duration
    assert original_live_read_duration is None

    # Make a revision, so we have both draft and live in existence
    revision = detail_page.save_revision()
    assert json.loads(revision.content_json)['estimated_read_duration'] == original_live_read_duration

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request,
        is_post_creation=True  # THIS will mean the live page is updated at the same time as the draft
    )

    detail_page.refresh_from_db()

    expected_duration = timedelta(seconds=4)  # NB just the read time of a skeleton DetailPage

    # show the live version is updated yet
    assert detail_page.estimated_read_duration == expected_duration
    assert detail_page.has_unpublished_changes is True

    # and the draft is updated too
    latest_rev = detail_page.get_latest_revision()
    assert revision == latest_rev
    assert json.loads(latest_rev.content_json)['estimated_read_duration'] == str(expected_duration)


@pytest.mark.parametrize('is_post_creation_val', (True, False))
@pytest.mark.django_db
def test__set_read_time__passes_through_is_post_creation(
    rf,
    domestic_homepage,
    is_post_creation_val,
):
    request = rf.get('/')
    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    with mock.patch(
        'core.wagtail_hooks._update_data_for_appropriate_version'
    ) as mocked_update_data_for_appropriate_version:

        wagtail_hooks._set_read_time(request, detail_page, is_post_creation=is_post_creation_val)

    expected_seconds = 4
    mocked_update_data_for_appropriate_version.assert_called_once_with(
        page=detail_page,
        force_page_update=is_post_creation_val,
        data_to_update={'estimated_read_duration': timedelta(seconds=expected_seconds)}
    )


@pytest.mark.django_db
@pytest.mark.parametrize('force_update', (False, True))
def test__update_data_for_appropriate_version(domestic_homepage, rf, force_update):
    request = rf.get('/')
    request.user = AnonymousUser()

    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    assert detail_page.live is True
    # Make a revision, so we have both draft and live in existence
    revision = detail_page.save_revision()
    assert detail_page.get_latest_revision() == revision

    assert detail_page.title != 'Dummy Title'
    assert json.loads(revision.content_json)['title'] == detail_page.title

    wagtail_hooks._update_data_for_appropriate_version(
        page=detail_page,
        force_page_update=force_update,
        data_to_update={'title': 'Dummy Title'}
    )

    revision.refresh_from_db()
    assert json.loads(revision.content_json)['title'] == 'Dummy Title'

    detail_page.refresh_from_db()
    if force_update:
        assert detail_page.title == 'Dummy Title'
    else:
        assert detail_page.title != 'Dummy Title'


@pytest.mark.django_db
def test_set_read_time__after_create_page(domestic_homepage, rf):
    request = rf.get('/')
    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    with mock.patch('core.wagtail_hooks._set_read_time') as mock__set_read_time:
        wagtail_hooks.set_read_time__after_create_page(request, detail_page)
    mock__set_read_time.assert_called_once_with(request, detail_page, is_post_creation=True)


@pytest.mark.django_db
def test_set_read_time__after_edit_page(domestic_homepage, rf):
    request = rf.get('/')
    detail_page = factories.DetailPageFactory(
        parent=domestic_homepage,
        template='learn/detail_page.html',
        body=[],
    )
    with mock.patch('core.wagtail_hooks._set_read_time') as mock__set_read_time:
        wagtail_hooks.set_read_time__after_edit_page(request, detail_page)
    mock__set_read_time.assert_called_once_with(request, detail_page)


def test_wagtail_transfer_custom_adapter_methods___get_relevant_s3_meta():
    mock_field = mock.Mock(name='mock_field')
    adapter = S3FileFieldAdapter(mock_field)

    mock_field_value = mock.Mock(name='mock_field_value')
    mock_field_value.storage.bucket.name = 'test-bucket-name'
    mock_field_value.name = 'test-bucket-key'
    # There are other attributes on the real object, eg 'url'

    mock_objectsummary_instance = mock.Mock(name='mock_objectsummary_instance')
    mock_objectsummary_instance.size = 1234567
    mock_objectsummary_instance.e_tag.replace.return_value = 'aabbccddeeff112233445566'
    # The double quoting is correct - ETags are meant to be double-quoted.
    # See https://tools.ietf.org/html/rfc2616#section-14.19

    mock_objectsummary_class = mock.Mock(name='mock ObjectSummary')
    mock_objectsummary_class.return_value = mock_objectsummary_instance

    with mock.patch('core.wagtail_hooks.s3.ObjectSummary', mock_objectsummary_class):
        meta = adapter._get_relevant_s3_meta(mock_field_value)

    mock_objectsummary_class.assert_called_once_with(
        'test-bucket-name',
        'test-bucket-key'
    )
    assert meta == {
        'size': 1234567,
        'hash': 'aabbccddeeff112233445566'
    }


@pytest.mark.parametrize(
    'etag_val,expected',
    (
        ('"aabbccddeeff112233445566"', 'aabbccddeeff112233445566'),
        ('aabbccddeeff112233445566', 'aabbccddeeff112233445566'),
        ("aabbccddeeff112233445566", 'aabbccddeeff112233445566'),  # noqa Q000  - this was deliberate
    )
)
def test_wagtail_transfer_custom_adapter_methods___get_file_hash(etag_val, expected):
    mock_field = mock.Mock(name='mock_field')
    adapter = S3FileFieldAdapter(mock_field)

    mock_objectsummary_instance = mock.Mock(name='mock_objectsummary_instance')
    mock_objectsummary_instance.size = 1234567
    mock_objectsummary_instance.e_tag = etag_val

    hash_ = adapter._get_file_hash(mock_objectsummary_instance)

    assert hash_ == expected


@pytest.mark.parametrize(
    'file_url,expected',
    (
        # See constants.AWS_S3_MAIN_HOSTNAME_OPTIONS
        (
            'https://w-t-test-bucket.s3.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
        (
            'http://w-t-test-bucket.s3.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
        (
            'https://w-t-test-bucket.s3.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
        (
            'https://w-t-test-bucket.s3.dualstack.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
        (
            'https://w-t-test-bucket.s3-accesspoint.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
        (
            'https://w-t-test-bucket.s3-accesspoint.dualstack.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4')
        ),
    )
)
def test_wagtail_transfer_custom_adapter_methods___get_imported_file_bucket_and_key(
    file_url,
    expected
):
    mock_field = mock.Mock(name='mock_field')
    adapter = S3FileFieldAdapter(mock_field)
    assert adapter._get_imported_file_bucket_and_key(file_url) == expected


@override_settings(MEDIA_URL='https://magna-fake-example.s3.amazonaws.com')
@pytest.mark.parametrize(
    'url,expected',
    (
        ('https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg', {
            'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
            'size': 123321,
            'hash': 'aabbccddeeff665544332211',
        }),
        (None, None),
    )
)
def test_wagtail_transfer_custom_adapter_methods__serialize(
    url,
    expected
):
    file_field = FileField()

    if url:
        mock_field_value = mock.Mock()
        mock_field_value.url = url
        # There are other attributes on the real object, but we're only using url here
    else:
        mock_field_value = None

    file_field.value_from_object = mock.Mock(return_value=mock_field_value)

    adapter = S3FileFieldAdapter(file_field)
    instance = mock.Mock()

    mock_get_relevant_s3_meta = mock.Mock(return_value={
        'download_url': url,
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'
    })

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        output = adapter.serialize(instance)

    assert output == expected

    file_field.value_from_object.assert_called_once_with(instance)

    if url:
        mock_get_relevant_s3_meta.assert_called_once_with(
            field_value=mock_field_value
        )

####################################################################################################
# Cases for S3FileFieldAdapter.populate_field

# These following tests are repetitive, but using parametrize() to DRY them up just
# made them really complex

# 1. File not already imported, source's hash matches hashes with existing file, so no import needed
# 2. File not already imported, source's hash doesn't match existing file, so we do a fresh import
# 3. As above, but an exception is raised during file.transfer()
# 4. File was already imported - no need to re-import
# 5. Null `value` param, we abandon early


def test_wagtail_transfer_custom_adapter_methods__populate_field__case_1():
    # 1. File not already imported, source's hash matches hashes with existing file, so no import needed
    file_field = FileField()
    file_field.get_attname = mock.Mock(return_value='some-filefield')

    mock_field_value = mock.Mock(name='mock_field_value')
    mock_field_value.storage.bucket.name = 'test-bucket-name'
    mock_field_value.name = 'test-bucket-key'
    file_field.value_from_object = mock.Mock(return_value=mock_field_value)

    adapter = S3FileFieldAdapter(file_field)

    fake_value = {
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_imported_file = mock.Mock(name='mock_imported_file')

    mock_get_relevant_s3_meta = mock.Mock(return_value={
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'  # same as existing file, so no import will happen
    })

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.return_value = mock_imported_file

    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    mock_instance = mock.Mock()

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        with mock.patch(
            'core.wagtail_hooks.S3WagtailTransferFile',
            mock_S3WagtailTransferFile
        ):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    assert adapter._get_imported_file_bucket_and_key.call_count == 0
    mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)
    assert mock_S3WagtailTransferFile.call_count == 0
    assert mock_s3_file.transfer.call_count == 0


def test_wagtail_transfer_custom_adapter_methods__populate_field__case_2():
    # 2. File not already imported, source's hash DOES NOT match existing file, so we do a fresh import
    file_field = FileField()
    file_field.get_attname = mock.Mock(return_value='some-filefield')

    mock_field_value = mock.Mock(name='mock_field_value')
    mock_field_value.storage.bucket.name = 'test-bucket-name'
    mock_field_value.name = 'test-bucket-key'

    file_field.value_from_object = mock.Mock(return_value=mock_field_value)

    mock_instance = mock.Mock()

    adapter = S3FileFieldAdapter(file_field)

    fake_value = {
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_imported_file = mock.Mock(name='mock_imported_file')

    mock_get_relevant_s3_meta = mock.Mock(return_value={
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'bbccddeeff'  # ie, does NOT match
    })

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.return_value = mock_imported_file

    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        with mock.patch(
            'core.wagtail_hooks.S3WagtailTransferFile',
            mock_S3WagtailTransferFile
        ):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    # the importer was called
    mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)

    adapter._get_imported_file_bucket_and_key.assert_called_once_with(
        fake_value['download_url']
    )

    mock_S3WagtailTransferFile.assert_called_once_with(
        local_filename='path/to/file.jpg',  # not changed by DefaultStorage in this test
        size=123321,
        hash_='aabbccddeeff665544332211',
        source_url='https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        source_bucket='magna-fake-example.s3.amazonaws.com',
        source_key='path/to/file.jpg',
    )

    mock_s3_file.transfer.assert_called_once_with()  # Deliberately no args

    # show the imported file is now in the cache so it won't be re-imported
    assert mock_context.imported_files_by_source_url[
        'MOCK_SOURCE_URL_VALUE'
    ] == mock_imported_file


def test_wagtail_transfer_custom_adapter_methods__populate_field__case_3():
    # 3. As above, but an exception is raised during file.transfer()
    file_field = FileField()
    file_field.get_attname = mock.Mock(return_value='some-filefield')

    mock_field_value = mock.Mock(name='mock_field_value')
    mock_field_value.storage.bucket.name = 'test-bucket-name'
    mock_field_value.name = 'test-bucket-key'

    file_field.value_from_object = mock.Mock(return_value=mock_field_value)

    mock_instance = mock.Mock()

    adapter = S3FileFieldAdapter(file_field)

    fake_value = {
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_get_relevant_s3_meta = mock.Mock(return_value={
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'bbccddeeff'  # ie, does NOT match
    })

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.side_effect = FileTransferError('Faked')
    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        with mock.patch(
            'core.wagtail_hooks.S3WagtailTransferFile',
            mock_S3WagtailTransferFile
        ):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    # the importer was called, but dudn't succeed
    mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)

    adapter._get_imported_file_bucket_and_key.assert_called_once_with(
        fake_value['download_url']
    )

    mock_S3WagtailTransferFile.assert_called_once_with(
        local_filename='path/to/file.jpg',  # not changed by DefaultStorage in this test
        size=123321,
        hash_='aabbccddeeff665544332211',
        source_url='https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        source_bucket='magna-fake-example.s3.amazonaws.com',
        source_key='path/to/file.jpg',
    )

    mock_s3_file.transfer.assert_called_once_with()  # Deliberately no args

    # show the imported file is NOT in the cache because we failde
    assert 'MOCK_SOURCE_URL_VALUE' not in mock_context.imported_files_by_source_url


def test_wagtail_transfer_custom_adapter_methods__populate_field__case_4():
    # 4. File was already imported - no need to re-import

    file_field = FileField()
    file_field.get_attname = mock.Mock(return_value='some-filefield')

    mock_field_value = mock.Mock(name='mock_field_value')
    mock_field_value.storage.bucket.name = 'test-bucket-name'
    mock_field_value.name = 'test-bucket-key'

    file_field.value_from_object = mock.Mock(return_value=mock_field_value)

    mock_instance = mock.Mock()

    adapter = S3FileFieldAdapter(file_field)

    fake_value = {
        'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        'size': 123321,
        'hash': 'aabbccddeeff665544332211'
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock()

    mock_imported_file = mock.Mock(name='mock_imported_file')
    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {
        'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg': mock_imported_file
    }

    mock_get_relevant_s3_meta = mock.Mock()
    mock_S3WagtailTransferFile = mock.Mock()  # noqa N806

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        with mock.patch(
            'core.wagtail_hooks.S3WagtailTransferFile',
            mock_S3WagtailTransferFile
        ):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    assert adapter._get_imported_file_bucket_and_key.call_count == 0
    assert mock_get_relevant_s3_meta.call_count == 0
    assert mock_S3WagtailTransferFile.call_count == 0


def test_wagtail_transfer_custom_adapter_methods__populate_field__case_5():
    # 5. Null `value` param, we abandon early

    file_field = FileField()
    file_field.get_attname = mock.Mock(return_value='some-filefield')

    file_field.value_from_object = mock.Mock()

    mock_instance = mock.Mock()

    adapter = S3FileFieldAdapter(file_field)

    fake_value = {}

    adapter._get_imported_file_bucket_and_key = mock.Mock()

    mock_context = mock.Mock()
    mock_get_relevant_s3_meta = mock.Mock()
    mock_S3WagtailTransferFile = mock.Mock()  # noqa N806

    with mock.patch(
        'core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta',
        mock_get_relevant_s3_meta
    ):
        with mock.patch(
            'core.wagtail_hooks.S3WagtailTransferFile',
            mock_S3WagtailTransferFile
        ):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    assert file_field.value_from_object.call_count == 0
    assert adapter._get_imported_file_bucket_and_key.call_count == 0
    assert mock_get_relevant_s3_meta.call_count == 0
    assert mock_S3WagtailTransferFile.call_count == 0

####################################################################################################


@override_settings(AWS_STORAGE_BUCKET_NAME='magna-fake-bucket-2')
@mock.patch('core.wagtail_hooks.s3.meta.client.copy')
@mock.patch('core.wagtail_hooks.ImportedFile.objects.create')
def test_s3wagtailtransferfile__transfer(
    mock_importedfile_objects_create,
    mock_s3_client_copy,
):

    file = S3WagtailTransferFile(
        local_filename='path/to/file.jpg',  # not changed by DefaultStorage in this test
        size=123321,
        hash_='aabbccddeeff665544332211',
        source_url='https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        source_bucket='magna-fake-bucket-1.s3.amazonaws.com',
        source_key='path/to/file.jpg',
    )

    assert file.local_filename == 'path/to/file.jpg'
    assert file.size == 123321
    assert file.hash == 'aabbccddeeff665544332211'
    assert file.source_url == 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg'
    assert file.source_bucket == 'magna-fake-bucket-1.s3.amazonaws.com'
    assert file.source_key == 'path/to/file.jpg'

    assert not mock_s3_client_copy.called

    file.transfer()

    mock_s3_client_copy.assert_called_once_with(
        {
            'Bucket': file.source_bucket,
            'Key': file.source_key
        },
        'magna-fake-bucket-2',
        file.local_filename,
    )

    mock_importedfile_objects_create.assert_called_once_with(
        file=file.local_filename,
        source_url=file.source_url,
        hash=file.hash,
        size=file.size,
    )


@pytest.mark.parametrize(
    'exception_class', (
        RetriesExceededError,
        S3UploadFailedError,
        ValueError,
    )
)
@mock.patch('core.wagtail_hooks.s3.meta.client.copy')
def test_s3wagtailtransferfile__transfer__covered_exceptions(mock_s3_client_copy, exception_class):
    file = S3WagtailTransferFile(
        local_filename='path/to/file.jpg',  # not changed by DefaultStorage in this test
        size=123321,
        hash_='aabbccddeeff665544332211',
        source_url='https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
        source_bucket='magna-fake-bucket-1.s3.amazonaws.com',
        source_key='path/to/file.jpg',
    )
    mock_s3_client_copy.side_effect = exception_class('Faked')

    with pytest.raises(FileTransferError):
        file.transfer()


@pytest.mark.parametrize(
    'user_media_on_s3,expected',
    (
        (True, {FileField: S3FileFieldAdapter}),
        (False, {}),
    )
)
def test_register_s3_media_file_adapter(user_media_on_s3, expected):
    with override_settings(USER_MEDIA_ON_S3=user_media_on_s3):
        assert register_s3_media_file_adapter() == expected
