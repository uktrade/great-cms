import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware

from core import wagtail_hooks
from tests.unit.learn.factories import LessonPageFactory


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
    assert response.url == '/signup/get-tailored-content/?next=/foo/bar/'


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
