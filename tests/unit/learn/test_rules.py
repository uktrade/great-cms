import pytest

from . import factories


@pytest.mark.django_db
def test_match_product_in_querystring(rf):
    rule = factories.MatchProductQuerystringFactory()
    request = rf.get(f'/?product={rule.product.name}')
    assert rule.test_user(request=request)


@pytest.mark.django_db
def test_not_match_product_in_querystring(rf):
    rule = factories.MatchProductQuerystringFactory()
    request = rf.get(f'/?product=bla')
    assert rule.test_user(request=request) is False


@pytest.mark.django_db
def test_match_country_in_querystring(rf):
    rule = factories.MatchCountryQuerystringFactory()
    request = rf.get(f'/?country={rule.country.name}')
    assert rule.test_user(request=request)


@pytest.mark.django_db
def test_not_match_country_in_querystring(rf):
    rule = factories.MatchCountryQuerystringFactory()
    request = rf.get(f'/?country=bla')
    assert rule.test_user(request=request) is False
