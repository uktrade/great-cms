from unittest.mock import mock_open, patch

import pytest
from django.core.management import call_command
from wagtail.contrib.redirects.models import Redirect


@pytest.mark.django_db
def test_call_update_redirects():
    mock_csv_content = """Current URL,New URL
    path/with/slash/,/new/path/with/slash/
    this/should/be/updated,/new/path/
    this/should/be/updated,/new/updated/path"""
    mock_csv_open = mock_open(read_data=mock_csv_content)
    with patch('builtins.open', mock_csv_open):
        call_command('update_redirects')

        # 2 Redirect objects because 'this/should/be/updated' gets created on first pass and then updated
        assert Redirect.objects.count() == 2

        # first redirect should have had slash placed at start and removed from end of current url
        assert Redirect.objects.filter(old_path='/path/with/slash').exists()

        # second redirect should have updated
        updated_redirect = Redirect.objects.get(old_path='/this/should/be/updated')
        assert updated_redirect.redirect_link == 'https://www.business.gov.uk/new/updated/path'


@pytest.mark.django_db
def test_call_update_redirects_custom_domain():
    mock_csv_content = """Current URL,New URL
    path/with/slash/,/new/path/with/slash/
    this/should/be/updated,/new/path/
    this/should/be/updated,/new/updated/path"""
    mock_csv_open = mock_open(read_data=mock_csv_content)
    with patch('builtins.open', mock_csv_open):
        call_command('update_redirects', redirect_to_domain='http://greatcms.trade.bgs')

        # 2 Redirect objects because 'this/should/be/updated' gets created on first pass and then updated
        assert Redirect.objects.count() == 2

        # first redirect should have had slash placed at start and removed from end of current url
        assert Redirect.objects.filter(old_path='/path/with/slash').exists()

        # second redirect should have updated
        updated_redirect = Redirect.objects.get(old_path='/this/should/be/updated')
        assert updated_redirect.redirect_link == 'http://greatcms.trade.bgs/new/updated/path'
