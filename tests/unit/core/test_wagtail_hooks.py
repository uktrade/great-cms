import json

from unittest import mock
from datetime import timedelta

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from wagtail.core.rich_text import RichText

from core import wagtail_hooks
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
