import pytest
from django.contrib.auth.models import AnonymousUser

from . import factories


@pytest.mark.django_db
def test_match_product_in_querystring(rf):
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get(f'/?product={rule.product.name}')
    request.user = AnonymousUser()
    assert rule.test_user(request=request)


@pytest.mark.django_db
def test_not_match_product_in_querystring(rf):
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get('/?product=bla')
    request.user = AnonymousUser()
    assert rule.test_user(request=request) is False


@pytest.mark.django_db
def test_match_product_in_expertise(rf, user, mock_get_company_profile):
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get('/')
    request.user = user

    mock_get_company_profile.return_value = {'expertise_products_services': {'other': [rule.product.name]}}

    assert rule.test_user(request=request) is True


@pytest.mark.django_db
def test_not_match_product_in_expertise(rf, user, mock_get_company_profile):
    mock_get_company_profile.return_value = {'expertise_products_services': {'other': ['foo']}}
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get('/')
    request.user = user

    assert rule.test_user(request=request) is False


@pytest.mark.django_db
def test_match_product_in_querystring_takes_precedence_over_user_expertise(rf, mock_get_company_profile, user):
    mock_get_company_profile.return_value = {'expertise_products_services': {'other': ['foo']}}
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get(f'/?product={rule.product.name}')
    request.user = user

    assert rule.test_user(request=request)


@pytest.mark.django_db
def test_match_product_no_company(rf, user):
    rule = factories.MatchProductExpertiseFactory()
    request = rf.get(f'/?product={rule.product.name}')
    request.user = user

    assert rule.test_user(request=request) is True


@pytest.mark.django_db
def test_match_country_in_querystring(rf):
    rule = factories.MatchCountryQuerystringFactory()
    request = rf.get(f'/?country={rule.country.name}')
    request.user = AnonymousUser()
    assert rule.test_user(request=request)


@pytest.mark.django_db
def test_not_match_country_in_querystring(rf):
    rule = factories.MatchCountryQuerystringFactory()
    request = rf.get('/?country=bla')
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
    rule = factories.MatchFirstCountryOfInterestFactory(country=factories.CountryFactory(name='Australia'))
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
