import datetime
import json
from datetime import timedelta
from unittest import mock

import pytest
from boto3.exceptions import RetriesExceededError, S3UploadFailedError
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import FileField
from django.test import TestCase, override_settings
from django.utils.safestring import mark_safe
from freezegun import freeze_time
from wagtail.admin.menu import DismissibleMenuItem
from wagtail.rich_text import RichText
from wagtail.tests.utils import WagtailPageTests

from config import settings
from core import cms_slugs, wagtail_hooks
from core.constants import MENU_ITEM_ADD_CAMPAIGN_SITE_LINK
from core.models import DetailPage, MicrositePage
from core.rich_text import (
    AnchorIdentifierLinkHandler,
    AnchorIndentifierEntityElementHandler,
    render_a,
)
from core.wagtail_hooks import (
    FileTransferError,
    MigratePage,
    S3FileFieldAdapter,
    S3WagtailTransferFile,
    convert_all_columns,
    convert_cta,
    convert_image,
    convert_quote,
    convert_related_links,
    convert_text,
    convert_video,
    editor_css,
    get_microsite_page_body,
    register_campaign_site_help_menu_item,
    register_s3_media_file_adapter,
    toolbar_sticky_by_default,
)
from tests.helpers import make_test_video
from tests.unit.core import factories
from tests.unit.core.factories import StructurePageFactory
from tests.unit.domestic.factories import ArticlePageFactory, CountryGuidePageFactory
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
def test_anonymous_user_required_handles_authenticated_users(rf, domestic_homepage, user, get_response):
    request = rf.get('/')
    request.user = user

    middleware = SessionMiddleware(get_response)
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
def test_login_required_signup_wizard_ignores_irrelevant_pages(rf, domestic_homepage):
    if not settings.FEATURE_DEA_V2:
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
def test_login_required_signup_wizard_handles_anonymous_users(rf, domestic_homepage, get_response):
    if not settings.FEATURE_DEA_V2:
        page = LessonPageFactory(parent=domestic_homepage)

        request = rf.get('/foo/bar/')
        request.user = AnonymousUser()
        middleware = SessionMiddleware(get_response)
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
def test_login_required_signup_wizard_handles_anonymous_users_opting_out(rf, domestic_homepage, user, get_response):
    if not settings.FEATURE_DEA_V2:
        page = LessonPageFactory(parent=domestic_homepage)

        first_request = rf.get('/foo/bar/', {'show-generic-content': True})
        first_request.user = AnonymousUser()

        middleware = SessionMiddleware(get_response)
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
    if not settings.FEATURE_DEA_V2:
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
        objective=[('paragraph', RichText(reading_content))],
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=182)

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(page=detail_page, request=request)

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
        objective=[('paragraph', RichText(reading_content))],
        body=[],  # if needed StreamField rich-text and video content can be added
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=205 + 101)  # reading + watching

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(page=detail_page, request=request)

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
        body=[],  # if needed StreamField rich-text and video content can be added
    )
    # Every real-world page will have a revision, so the test needs one, too
    revision = detail_page.save_revision()
    revision.publish()

    expected_duration = timedelta(seconds=57 + 100)  # reading + watching

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != expected_duration

    wagtail_hooks._set_read_time(page=detail_page, request=request)

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration == expected_duration


@pytest.mark.django_db
def test_estimated_read_time_calculation__updates_only_draft_if_appropriate(rf, domestic_homepage):
    # IF THIS TEST FAILS BASED ON OFF-BY-ONE-SECOND DURATIONS... check whether
    # your changeset has slightly increased the size of the HTML page, which
    # may have slightly pushed up the default/empty-page readtime (either in
    # real terms or just in terms of elements that affect the calculation). If
    # so, pushing up the expected time variables in the test is OK to do.

    request = rf.get('/')
    request.user = AnonymousUser()

    video_for_hero = make_test_video(duration=125)
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
    assert revision.content['estimated_read_duration'] == original_live_read_duration

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(page=detail_page, request=request)

    detail_page.refresh_from_db()

    expected_duration = timedelta(seconds=52)  # NB just the read time of a skeleton DetailPage

    # show the live version is not updated yet
    assert detail_page.has_unpublished_changes is True
    assert detail_page.estimated_read_duration != expected_duration
    assert detail_page.estimated_read_duration == original_live_read_duration

    # but the draft is
    latest_rev = detail_page.get_latest_revision()
    assert revision == latest_rev

    if isinstance(latest_rev.content, str):
        json_object = json.loads(latest_rev.content)
        latest_rev.content = json_object
    assert latest_rev.content['estimated_read_duration'] == str(expected_duration)

    if 'title' not in latest_rev.content or not latest_rev.content['title']:
        latest_rev.content['title'] = 'Test Title'

    if 'template' not in latest_rev.content or not latest_rev.content['template']:
        latest_rev.content['template'] = 'learn/detail_page.html'

    # Now publish the draft and show it updates the live, too

    latest_rev.publish()

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(page=detail_page, request=request)

    detail_page.refresh_from_db()
    assert detail_page.estimated_read_duration != original_live_read_duration

    # NOTE: for a reason unrelated to the point of _this_ test, the readtime
    # of the published page CAN BE calculated as slightly longer than the draft.
    # This may be in part due to the page having a very small amount of content.
    assert detail_page.estimated_read_duration == timedelta(seconds=32)


@pytest.mark.django_db
def test_estimated_read_time_calculation__forced_update_of_live(rf, domestic_homepage):
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
    assert revision.content['estimated_read_duration'] == original_live_read_duration

    detail_page.refresh_from_db()

    wagtail_hooks._set_read_time(
        page=detail_page,
        request=request,
        is_post_creation=True,  # THIS will mean the live page is updated at the same time as the draft
    )

    detail_page.refresh_from_db()

    expected_duration = timedelta(seconds=32)  # NB just the read time of a skeleton DetailPage

    # show the live version is updated yet
    assert detail_page.estimated_read_duration == expected_duration
    assert detail_page.has_unpublished_changes is True

    # and the draft is updated too
    latest_rev = detail_page.get_latest_revision()
    assert revision == latest_rev
    assert latest_rev.content['estimated_read_duration'] == str(expected_duration)


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

    expected_seconds = 32
    mocked_update_data_for_appropriate_version.assert_called_once_with(
        page=detail_page,
        force_page_update=is_post_creation_val,
        data_to_update={'estimated_read_duration': timedelta(seconds=expected_seconds)},
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
    assert revision.content['title'] == detail_page.title

    wagtail_hooks._update_data_for_appropriate_version(
        page=detail_page, force_page_update=force_update, data_to_update={'title': 'Dummy Title'}
    )

    revision.refresh_from_db()

    if isinstance(revision.content, str):
        jason_content = json.loads(revision.content)
        revision.content = jason_content

    assert revision.content['title'] == 'Dummy Title'

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

    mock_objectsummary_class.assert_called_once_with('test-bucket-name', 'test-bucket-key')
    assert meta == {'size': 1234567, 'hash': 'aabbccddeeff112233445566'}


@pytest.mark.parametrize(
    'etag_val,expected',
    (
        ('"aabbccddeeff112233445566"', 'aabbccddeeff112233445566'),
        ('aabbccddeeff112233445566', 'aabbccddeeff112233445566'),
        ("aabbccddeeff112233445566", 'aabbccddeeff112233445566'),  # noqa Q000  - this was deliberate
    ),
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
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
        (
            'http://w-t-test-bucket.s3.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
        (
            'https://w-t-test-bucket.s3.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
        (
            'https://w-t-test-bucket.s3.dualstack.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
        (
            'https://w-t-test-bucket.s3-accesspoint.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
        (
            'https://w-t-test-bucket.s3-accesspoint.dualstack.eu-west-2.amazonaws.com/media/path/to/file.mp4',
            ('w-t-test-bucket', 'media/path/to/file.mp4'),
        ),
    ),
)
def test_wagtail_transfer_custom_adapter_methods___get_imported_file_bucket_and_key(file_url, expected):
    mock_field = mock.Mock(name='mock_field')
    adapter = S3FileFieldAdapter(mock_field)
    assert adapter._get_imported_file_bucket_and_key(file_url) == expected


@override_settings(MEDIA_URL='https://magna-fake-example.s3.amazonaws.com')
@pytest.mark.parametrize(
    'url,expected',
    (
        (
            'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
            {
                'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
                'size': 123321,
                'hash': 'aabbccddeeff665544332211',
            },
        ),
        (None, None),
    ),
)
def test_wagtail_transfer_custom_adapter_methods__serialize(url, expected):
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

    mock_get_relevant_s3_meta = mock.Mock(
        return_value={'download_url': url, 'size': 123321, 'hash': 'aabbccddeeff665544332211'}
    )

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        output = adapter.serialize(instance)

    assert output == expected

    file_field.value_from_object.assert_called_once_with(instance)

    if url:
        mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)


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
        'hash': 'aabbccddeeff665544332211',
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_imported_file = mock.Mock(name='mock_imported_file')

    mock_get_relevant_s3_meta = mock.Mock(
        return_value={
            'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
            'size': 123321,
            'hash': 'aabbccddeeff665544332211',  # same as existing file, so no import will happen
        }
    )

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.return_value = mock_imported_file

    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    mock_instance = mock.Mock()

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        with mock.patch('core.wagtail_hooks.S3WagtailTransferFile', mock_S3WagtailTransferFile):
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
        'hash': 'aabbccddeeff665544332211',
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_imported_file = mock.Mock(name='mock_imported_file')

    mock_get_relevant_s3_meta = mock.Mock(
        return_value={
            'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
            'size': 123321,
            'hash': 'bbccddeeff',  # ie, does NOT match
        }
    )

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.return_value = mock_imported_file

    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        with mock.patch('core.wagtail_hooks.S3WagtailTransferFile', mock_S3WagtailTransferFile):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    # the importer was called
    mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)

    adapter._get_imported_file_bucket_and_key.assert_called_once_with(fake_value['download_url'])

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
    assert mock_context.imported_files_by_source_url['MOCK_SOURCE_URL_VALUE'] == mock_imported_file


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
        'hash': 'aabbccddeeff665544332211',
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock(
        return_value=('magna-fake-example.s3.amazonaws.com', 'path/to/file.jpg')
    )

    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {}

    mock_get_relevant_s3_meta = mock.Mock(
        return_value={
            'download_url': 'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg',
            'size': 123321,
            'hash': 'bbccddeeff',  # ie, does NOT match
        }
    )

    mock_s3_file = mock.Mock(name='mock_s3_file')
    mock_s3_file.source_url = 'MOCK_SOURCE_URL_VALUE'
    mock_s3_file.transfer.side_effect = FileTransferError('Faked')
    mock_S3WagtailTransferFile = mock.Mock(return_value=mock_s3_file)  # noqa N806

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        with mock.patch('core.wagtail_hooks.S3WagtailTransferFile', mock_S3WagtailTransferFile):
            adapter.populate_field(
                instance=mock_instance,
                value=fake_value,
                context=mock_context,
            )

    # the importer was called, but dudn't succeed
    mock_get_relevant_s3_meta.assert_called_once_with(field_value=mock_field_value)

    adapter._get_imported_file_bucket_and_key.assert_called_once_with(fake_value['download_url'])

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
        'hash': 'aabbccddeeff665544332211',
    }

    adapter._get_imported_file_bucket_and_key = mock.Mock()

    mock_imported_file = mock.Mock(name='mock_imported_file')
    mock_context = mock.Mock()
    mock_context.imported_files_by_source_url = {
        'https://magna-fake-example.s3.amazonaws.com/path/to/file.jpg': mock_imported_file
    }

    mock_get_relevant_s3_meta = mock.Mock()
    mock_S3WagtailTransferFile = mock.Mock()  # noqa N806

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        with mock.patch('core.wagtail_hooks.S3WagtailTransferFile', mock_S3WagtailTransferFile):
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

    with mock.patch('core.wagtail_hooks.S3FileFieldAdapter._get_relevant_s3_meta', mock_get_relevant_s3_meta):
        with mock.patch('core.wagtail_hooks.S3WagtailTransferFile', mock_S3WagtailTransferFile):
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
        {'Bucket': file.source_bucket, 'Key': file.source_key},
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
    'exception_class',
    (
        RetriesExceededError,
        S3UploadFailedError,
        ValueError,
    ),
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
    ),
)
def test_register_s3_media_file_adapter(user_media_on_s3, expected):
    with override_settings(USER_MEDIA_ON_S3=user_media_on_s3):
        assert register_s3_media_file_adapter() == expected


def _fake_static(value):
    return '/path/to/static/' + value


@mock.patch('core.wagtail_hooks.static')
def test_case_study_editor_css(mock_static):
    mock_static.side_effect = _fake_static
    assert editor_css() == '<link rel="stylesheet" href="/path/to/static/cms-admin/css/case-study.css">'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'request_path',
    (
        '/test/path/',
        '/test/path/?token=test',
    ),
)
def test_authenticated_user_required__sets_next_param(rf, request_path):
    if not settings.FEATURE_DEA_V2:
        instance = DetailPage()
        assert instance.authenticated_user_required_redirect_url == cms_slugs.SIGNUP_URL

        request = rf.get(request_path)
        request.user = AnonymousUser()
        output = wagtail_hooks.authenticated_user_required(instance, request, [], {})

        assert output.status_code == 302
        assert output.headers['Location'] == f'{cms_slugs.SIGNUP_URL}?next={request_path}'


class MigrateArticeToMicrositeTestCase(WagtailPageTests, TestCase):
    @pytest.fixture(autouse=True)
    def domestic_homepage_fixture(self, domestic_homepage):
        self.domestic_homepage = domestic_homepage

    def setUp(self):
        self.parent_page = StructurePageFactory(parent=self.domestic_homepage, title='campaigns', slug='campaigns')
        article_body1 = json.dumps(
            [
                {'type': 'Video', 'value': {'video': 44}, 'id': 'b965f2ea-c030-41ff-b121-32895a0b7cb0'},
                {'type': 'image', 'value': 682, 'id': '5a176e7e-4fa8-42b5-b89e-202d8946910c'},
                {
                    'type': 'pull_quote',
                    'value': {
                        'quote': 'my quote',
                        'attribution': 'random guy',
                        'role': 'head',
                        'organisation': 'dit',
                        'organisation_link': 'http://www.google.com',
                    },
                    'id': 'e5632d7b-04f2-44ec-ae40-31e7c2e52c21',
                },
                {
                    'type': 'Columns',
                    'value': [
                        {
                            'type': 'column',
                            'value': {
                                'title': 'col1',
                                'image': None,
                                'description': '<p data-block-key="8vbdd9">sddsds</p>',
                                'link': 'www.google.com',
                            },
                            'id': '40839277-ef3d-461d-abbd-6506b08c80b6',
                        },
                        {
                            'type': 'column',
                            'value': {
                                'title': 'col2',
                                'image': None,
                                'description': '<p data-block-key="8vbd9">sddsds</p>',
                                'link': 'www.google.com',
                            },
                            'id': '40839277-ef3d-461d-abbd-6506b08c80b6',
                        },
                        {
                            'type': 'column',
                            'value': {
                                'title': 'col3',
                                'image': None,
                                'description': '<p data-block-key="8vdbd9">col3</p>',
                                'link': 'www.google.com',
                            },
                            'id': '40839277-ef3d-461d-abbd-6506b08c80b6',
                        },
                    ],
                },
                {
                    'type': 'text',
                    'value': '<p data-block-key="r0g5h">dssdsdds</p>',
                    'id': '55d0ff59-bcfd-46d9-9c02-b1977eed3f80',
                },
                {
                    'type': 'cta',
                    'value': {
                        'title': 'cta title',
                        'teaser': 'cta teaser',
                        'link_label': 'cta button',
                        'link': 'www.google.com',
                    },
                    'id': 'a5fc7270-aa4c-4057-9a12-2c4c3e69c19f',
                },
            ]
        )

        self.article1 = ArticlePageFactory(
            slug='test-article-bulk-action',
            article_body=article_body1,
            parent=self.parent_page,
            article_title='test',
            article_subheading='subheading',
            article_teaser='teaser',
            related_page_two_title='test title',
            related_page_two_link='www.google.ocm',
        )

        self.microsite_page = MicrositePage(slug='wrong-type', title='wrong page', page_title='test')
        self.parent_page.add_child(instance=self.microsite_page)

    def test_convert_quote(self):
        converted_quote = convert_quote(
            [block for block in self.article1.article_body if block.block_type == 'pull_quote'][0]
        )
        self.assertEqual(converted_quote['value']['quote'], 'my quote')
        self.assertEqual(converted_quote['type'], 'pull_quote')
        self.assertEqual(converted_quote['value']['attribution'], 'random guy')
        self.assertEqual(converted_quote['value']['role'], 'head')
        self.assertEqual(converted_quote['value']['organisation'], 'dit')
        self.assertEqual(converted_quote['value']['organisation_link'], 'http://www.google.com')

    def test_convert_text(self):
        text_block = convert_text([block for block in self.article1.article_body if block.block_type == 'text'][0])
        self.assertEqual(text_block['type'], 'text')
        self.assertEqual(text_block['value'], '<p data-block-key="r0g5h">dssdsdds</p>')

    def test_convert_columns(self):
        columns = convert_all_columns(
            [block for block in self.article1.article_body if block.block_type == 'Columns'][0]
        )
        self.assertEqual(len(columns['value']), 3)
        self.assertEqual(columns['value'][0]['type'], 'column')
        self.assertEqual(columns['value'][0]['value']['text'], '<p data-block-key="8vbdd9">sddsds</p>')
        self.assertEqual(columns['value'][0]['value']['button_label'], None)
        self.assertEqual(columns['value'][0]['value']['button_url'], 'www.google.com')

    def test_convert_related_links(self):
        related_links = convert_related_links(self.article1)
        self.assertEqual(len(related_links), 1)
        self.assertEqual(related_links[0]['type'], 'link')
        self.assertEqual(related_links[0]['value']['title'], 'test title')

    def test_convert_cta(self):
        cta = convert_cta([block for block in self.article1.article_body if block.block_type == 'cta'][0])
        self.assertEqual(cta['type'], 'cta')
        self.assertEqual(cta['value']['title'], 'cta title')
        self.assertEqual(cta['value']['teaser'], 'cta teaser')
        self.assertEqual(cta['value']['link_label'], 'cta button')
        self.assertEqual(cta['value']['link'], 'www.google.com')

    def test_get_microsite_page_body(self):
        page_body = get_microsite_page_body(self.article1.article_body)
        self.assertEqual(len(page_body), 6)
        self.assertEqual(len([item for item in page_body if item['type'] == 'form']), 0)
        self.assertEqual(len([item for item in page_body if item['type'] == 'pull_quote']), 1)
        self.assertEqual(len([item for item in page_body if item['type'] == 'cta']), 1)
        self.assertEqual(len([item for item in page_body if item['type'] == 'columns']), 1)
        self.assertEqual(len([item for item in page_body if item['type'] == 'text']), 1)
        self.assertEqual(len([item for item in page_body if item['type'] == 'video']), 1)

    def test_migrating_wrong_page_type(self):
        with self.assertRaises(NotImplementedError) as context:
            MigratePage.execute_action([self.microsite_page])
            self.assertTrue(context.msg is None)

    def test_convert_video(self):
        video = convert_video([block for block in self.article1.article_body if block.block_type == 'Video'][0])
        self.assertEqual(video['type'], 'video')

    def test_convert_image(self):
        image = convert_image([block for block in self.article1.article_body if block.block_type == 'image'][0])
        self.assertEqual(image['type'], 'image')

    def test_migrate_article_page(self):
        self.assertEqual(MigratePage.execute_action([self.article1]), (1, 1))


class WagtailInsertEditorJsTestCase(TestCase):
    def test_toolbar_sticky_by_default(self):
        return_value = toolbar_sticky_by_default()
        expected_value = mark_safe(
            """
        <script>
            if (window.localStorage.getItem("wagtail:draftail-toolbar")==null) {
                window.localStorage.setItem("wagtail:draftail-toolbar", "sticky");
            };
        </script>
        """
        )
        assert return_value == expected_value


def test_register_campaign_site_help_menu_item():
    actual = register_campaign_site_help_menu_item()

    assert isinstance(actual, DismissibleMenuItem)
    assert actual.label == 'Campaign Site, getting started'
    assert actual.url == MENU_ITEM_ADD_CAMPAIGN_SITE_LINK
    assert actual.icon_name == 'help'
    assert actual.order == 900
    assert actual.attrs == {
        'target': '_blank',
        'rel': 'noreferrer',
        'data-w-dismissible-id-value': 'campaign-site',
        'data-controller': 'w-dismissible',
        'data-w-dismissible-dismissed-class': 'w-dismissible--dismissed',
    }
    assert actual.name == 'campaign-site'


def test_render_a():
    attrs = {'id': 'test-id'}
    result = render_a(attrs)
    assert 'id="test-id"' in result
    assert 'data-id="test-id"' in result


def test_anchor_identifier_link_handler():
    handler = AnchorIdentifierLinkHandler()
    attrs = {'id': 'test-id'}
    result = handler.expand_db_attributes(attrs)
    assert 'id="test-id"' in result


def test_anchor_identifier_entity_element_handler():
    handler = AnchorIndentifierEntityElementHandler('ANCHOR-IDENTIFIER')
    attrs = {'href': '#test-id', 'id': 'test-id'}
    data = handler.get_attribute_data(attrs)
    assert data['anchor'] == 'test-id'
    assert data['data-id'] in 'test-id'
    assert handler.mutability == 'MUTABLE'


@freeze_time('2024-01-01 01:00:00')
@pytest.mark.django_db
def test_set_default_expiry_date(rf, domestic_homepage):
    request = rf.get('/')
    request.user = AnonymousUser()
    now = datetime.datetime.now()
    expected_date = now.replace(year=now.year + 1)

    microsite = factories.MicrositeFactory(
        title='Microsite',
        parent=domestic_homepage,
    )

    microsite_page = factories.MicrositePageFactory(
        slug='microsite-page',
        title='Test',
        page_title='Test',
        parent=microsite,
    )

    microsite_page_with_expire_date = factories.MicrositePageFactory(
        slug='microsite-page-with-expire-date',
        title='Test',
        page_title='Test',
        parent=microsite,
        expire_at=expected_date,
    )

    assert microsite_page.expire_at is None
    assert microsite_page_with_expire_date.expire_at == expected_date

    wagtail_hooks.set_default_expiry_date(page=microsite_page, request=request)
    wagtail_hooks.set_default_expiry_date(page=microsite_page_with_expire_date, request=request)

    assert microsite_page.expire_at is not None
    assert microsite_page.expire_at.date() == expected_date.date()
    assert microsite_page_with_expire_date.expire_at == expected_date


@mock.patch('django.contrib.messages.add_message')
@pytest.mark.django_db
def test_after_edit_page(mock_add_message, domestic_homepage, rf):
    request = rf.post(path='/')
    country_guide_page = CountryGuidePageFactory(
        parent=domestic_homepage,
    )
    wagtail_hooks.after_edit_page(request, country_guide_page)
    assert mock_add_message.call_count == 1
