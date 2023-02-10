import pytest
from django.contrib.auth.models import AnonymousUser

from export_academy.middleware import ExportAcademyRegistrationMiddleware
from tests.unit.export_academy import factories


@pytest.mark.django_db
def test_export_academy_middleware_does_not_trigger(rf, domestic_homepage, domestic_site):
    request = rf.get(domestic_homepage.url)
    middleware = ExportAcademyRegistrationMiddleware()

    middleware.process_request(request)

    assert hasattr(request, 'is_export_academy_registered') is False


@pytest.mark.django_db
def test_export_academy_middleware_user_unregistered(rf, export_academy_landing_page, export_academy_site):
    request = rf.get(export_academy_landing_page.url)
    request.user = AnonymousUser()
    middleware = ExportAcademyRegistrationMiddleware()

    middleware.process_request(request)

    assert request.is_export_academy_registered is False


@pytest.mark.django_db
def test_export_academy_middleware_user_registered(rf, user, export_academy_landing_page, export_academy_site):
    factories.RegistrationFactory(email=user.email)

    request = rf.get(export_academy_landing_page.url)
    request.user = user
    middleware = ExportAcademyRegistrationMiddleware()

    middleware.process_request(request)

    assert request.is_export_academy_registered is True
