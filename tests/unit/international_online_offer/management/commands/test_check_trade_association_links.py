from unittest import mock

import pytest
from django.core.management import call_command
from requests.exceptions import SSLError

from international_online_offer.models import TradeAssociation
from tests.unit.core.test_helpers import create_response
from tests.unit.international_online_offer.factories import TradeAssociationFactory


@pytest.mark.django_db
def test_check_page_found_valid_url():
    trade_association = TradeAssociationFactory(website_link='https://www.gov.uk')
    call_command('check_trade_association_links')
    assert TradeAssociation.objects.get(id=trade_association.id).link_valid


@pytest.mark.django_db
def test_check_page_found_missing_scheme():
    trade_association = TradeAssociationFactory(website_link='gov.uk')
    call_command('check_trade_association_links')
    assert TradeAssociation.objects.get(id=trade_association.id).link_valid


@mock.patch(
    'international_online_offer.management.commands.check_trade_association_links.requests.request',
    side_effect=[SSLError, create_response(200)],
)
@pytest.mark.django_db
def test_check_page_found_ssl_error(mock_request):
    trade_association = TradeAssociationFactory(website_link='https://www.gov.uk')

    call_command('check_trade_association_links')

    # the second request (inside the SSLError exception handling) should be called with verify=False
    assert mock_request._mock_call_args_list[1][1]['verify'] is False

    assert TradeAssociation.objects.get(id=trade_association.id).link_valid


@pytest.mark.django_db
def test_check_page_found_invalid_url():
    trade_association = TradeAssociationFactory(website_link='abcdefg')
    call_command('check_trade_association_links')
    assert TradeAssociation.objects.get(id=trade_association.id).link_valid is False
