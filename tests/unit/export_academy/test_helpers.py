import pytest
from django.contrib.auth.models import AnonymousUser

from export_academy.helpers import is_export_academy_registered
from tests.unit.export_academy import factories


@pytest.mark.django_db
def test_is_export_academy_unregistered():
    user = AnonymousUser()

    assert is_export_academy_registered(user) is False


@pytest.mark.django_db
def test_is_export_academy_registered(user):
    factories.RegistrationFactory(email=user.email)

    assert is_export_academy_registered(user) is True
