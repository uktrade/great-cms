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


@pytest.mark.django_db
def test_not_match_country_of_interest(rf, user):
    rule = factories.MatchFirstCountryOfInterestFactory()
    request = rf.get('/')
    request.user = user
    assert rule.test_user(request=request) is False


@pytest.mark.django_db
def test_match_country_of_interest(rf, user, mock_get_company_profile):
    mock_get_company_profile.return_value = {'expertise_countries': ['AU']}
    rule = factories.MatchFirstCountryOfInterestFactory(
        country=factories.CountryFactory(name='Australia')
    )
    request = rf.get('/')
    request.user = user
    assert rule.test_user(request=request) is True


@pytest.mark.django_db
def test_match_industry_of_interest(rf, user):
    rule = factories.MatchFirstIndustryOfInterestFactory(industry='SL10002')

    request = rf.get('/')
    request.user = user

    assert rule.test_user(request=request) is False


@pytest.mark.django_db
def test_not_match_industry_of_interest(rf, user, mock_get_company_profile):
    mock_get_company_profile.return_value = {'expertise_industries': ['SL10002']}

    rule = factories.MatchFirstIndustryOfInterestFactory(industry='SL10002')

    request = rf.get('/')
    request.user = user

    assert rule.test_user(request=request) is True
