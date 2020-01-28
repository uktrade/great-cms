from sso import models


def test_user_get_username():
    user = models.BusinessSSOUser(email='test@example.com')

    assert user.get_username() == 'test@example.com'


def test_user_save():
    user = models.BusinessSSOUser(email='test@example.com')

    assert user.save() is None
