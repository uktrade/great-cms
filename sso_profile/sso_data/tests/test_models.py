from unittest import mock

import pytest
from sso_data import models

from directory_constants import user_roles
from sso_profile.profile.business_profile import helpers


def test_full_name_empty():
    user = models.SSOUser()

    assert user.full_name is None


def test_full_name():
    user = models.SSOUser(first_name='Jim', last_name='Example')

    assert user.full_name == 'Jim Example'


@mock.patch.object(models.SSOUser, 'supplier', new_callable=mock.PropertyMock)
def test_is_company_admin_no_supplier(mock_supplier):
    mock_supplier.return_value = None
    assert models.SSOUser().is_company_admin is False


@pytest.mark.parametrize(
    'role,expected', ((user_roles.ADMIN, True), (user_roles.EDITOR, False), (user_roles.MEMBER, False))
)
@mock.patch.object(models.SSOUser, 'supplier', new_callable=mock.PropertyMock)
def test_is_company_admin(mock_supplier, role, expected):
    mock_supplier.return_value = {'role': role}
    assert models.SSOUser().is_company_admin is expected


@mock.patch.object(helpers, 'get_supplier_profile')
def test_supplier(mock_get_supplier_profile):
    user = models.SSOUser(session_id='1234')
    user.id = 100

    assert user.supplier
    assert mock_get_supplier_profile.call_count == 1
    assert mock_get_supplier_profile.call_args == mock.call(100)
