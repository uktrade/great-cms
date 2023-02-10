import pytest

from .factories import EventFactory, RegistrationFactory


@pytest.mark.parametrize(
    'factory,attrs',
    ((EventFactory, ['id', 'name']), (RegistrationFactory, ['email'])),
)
@pytest.mark.django_db
def test_model_to_string(factory, attrs):
    instance = factory()
    assert str(instance) == ':'.join([str(getattr(instance, attr)) for attr in attrs])
