import pytest
from django.contrib.auth import get_user_model


@pytest.mark.mvp_only
@pytest.mark.django_db
def test_newly_created_user_promoted_to_superuser():
    User = get_user_model()
    user = User(username='test', is_staff=False, is_superuser=False)
    user.save()
    assert user.is_staff is True
    assert user.is_superuser is True
