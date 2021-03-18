import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from wagtail.core.rich_text import RichText

from core import cms_slugs, snippet_slugs
from domestic.models import TradeFinanceSnippet


@pytest.mark.django_db
def test_landing_page_not_logged_in(client, user, domestic_site):
    response = client.get('/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_page_logged_in(client, user, domestic_site):

    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 302
    assert response.url == cms_slugs.DASHBOARD_URL


@pytest.mark.django_db
def test_trade_finance_view(client):

    snippet = TradeFinanceSnippet(
        slug=snippet_slugs.GREAT_TRADE_FINANCE,
        breadcrumbs_label='Trade Finance Test Breadcrumb',
        hero_text=RichText('<h1>Hero Text</h1>'),
        contact_proposition=RichText('<p>contact proposition</p>'),
        contact_button='contact button text',
        advantages_title='advantages title',
        evidence=RichText('<p>evidence evidence evidence</p>'),
    )
    snippet.save()

    dest = reverse('domestic:trade-finance')

    response = client.get(dest)
    assert response.status_code == 200

    for val in [
        b'Trade Finance Test Breadcrumb',
        b'<h1>Hero Text</h1>',
        b'<p>contact proposition</p>',
        b'contact button text',
        b'advantages title',
        b'<p>evidence evidence evidence</p>',
    ]:
        assert val in response.content

    assertTemplateUsed(response, 'domestic/finance/trade_finance.html')
