from unittest import mock

from directory_constants import choices
import pytest

from django.urls import reverse
from django.conf import settings

from directory_components import helpers


@pytest.mark.parametrize('target,expected', (
    ('example.com', 'example.com?next=next.com'),
    ('example.com?next=existing.com', 'example.com?next=existing.com'),
    ('example.com?a=b', 'example.com?a=b&next=next.com'),
    ('example.com?a=b&next=existing.com', 'example.com?a=b&next=existing.com'),
))
def test_add_next(target, expected):
    next_url = 'next.com'
    assert helpers.add_next(target, next_url) == expected


def test_build_social_links(rf):
    social_links_builder = helpers.SocialLinkBuilder(
        url='http://testserver/',
        page_title='Do research first',
        app_title='Export Readiness',
    )

    assert social_links_builder.links['twitter'] == (
        'https://twitter.com/intent/tweet'
        '?text=Export%20Readiness%20-%20Do%20research%20first%20'
        'http://testserver/'
    )
    assert social_links_builder.links['facebook'] == (
        'https://www.facebook.com/share.php?u=http://testserver/'
    )
    assert social_links_builder.links['linkedin'] == (
        'https://www.linkedin.com/shareArticle?mini=true&'
        'url=http://testserver/&'
        'title=Export%20Readiness%20-%20Do%20research%20first%20'
        '&source=LinkedIn'
    )
    assert social_links_builder.links['email'] == (
        'mailto:?body=http://testserver/'
        '&subject=Export%20Readiness%20-%20Do%20research%20first%20'
    )


@pytest.mark.parametrize('country_code,country_name', choices.COUNTRY_CHOICES)
def test_get_country_from_querystring(country_code, country_name, rf):
    url = reverse('index')
    request = rf.get(url, {'country': country_code})

    actual = helpers.get_country_from_querystring(request)

    assert actual == country_code


def test_get_country_from_querystring_invalid_code(rf):
    url = reverse('index')
    request = rf.get(url, {'country': 'foo'})

    actual = helpers.get_country_from_querystring(request)

    assert not actual


@pytest.mark.parametrize('mock_get', (
    {'country': ''},
    {},
))
def test_get_cookie_when_no_querystring(mock_get, rf):
    settings.COUNTRY_COOKIE_NAME = 'country'
    url = reverse('index')
    request = rf.get(url, mock_get)
    request.COOKIES = {'country': 'GB'}
    actual = helpers.get_user_country(request)

    assert actual == 'GB'


@pytest.mark.parametrize('value,expected', (
    ('2019-01-31', '31 January 2019'),
    ('', None),
    (None, None),
))
def test_profile_parser_date_of_creation(value, expected):
    parser = helpers.CompanyParser({'date_of_creation': value})
    assert parser.date_of_creation == expected


@pytest.mark.parametrize('value,expected', (
    (
        {
            'address_line_1': '123 Fake street',
            'address_line_2': 'Fakeville',
            'locality': 'Fakeshire',
            'postal_code': 'FAK ELA'
        },
        '123 Fake street, Fakeville, Fakeshire, FAK ELA'
    ),
    (
        {
            'address_line_1': '123 Fake street',
            'locality': 'Fakeshire',
            'postal_code': 'FAK ELA'
        },
        '123 Fake street, Fakeshire, FAK ELA'
    ),
    (
        {
            'address_line_1': '123 Fake street',
            'address_line_2': 'Fakeville',
            'postal_code': 'FAK ELA'
        },
        '123 Fake street, Fakeville, FAK ELA'
    ),
))
def test_profile_parser_address(value, expected):
    parser = helpers.CompanyParser(value)
    assert parser.address == expected


@pytest.mark.parametrize('value', ('', None))
@mock.patch.object(helpers, 'tokenize_keywords')
def test_profile_parser_keywords_no_keyword(mock_tokenize_keywords, value):
    parser = helpers.CompanyParser({'keywords': value})

    parser.keywords

    assert mock_tokenize_keywords.call_count == 0


@mock.patch.object(helpers, 'tokenize_keywords')
def test_profile_parser_keywords(mock_tokenize_keywords):
    parser = helpers.CompanyParser({'keywords': 'thing,other'})

    parser.keywords

    assert mock_tokenize_keywords.call_count == 1
    assert mock_tokenize_keywords.call_args == mock.call('thing,other')


def test_profile_parser_keywords_joined():
    parser = helpers.CompanyParser({'keywords': 'thing,other'})

    assert parser.keywords == 'thing, other'


@pytest.mark.parametrize('value,expected', (
    (None, ''),
    ('', ''),
    (['AEROSPACE'], 'Aerospace'),
))
def test_profile_parser_sectors(value, expected):
    parser = helpers.CompanyParser({'sectors': value})

    assert parser.sectors_label == expected


@pytest.mark.parametrize('value,expected', (
    (None, None),
    ('', None),
    ('1-10', '1-10'),
))
def test_profile_parser_employees_label(value, expected):
    parser = helpers.CompanyParser({'employees': value})

    assert parser.employees_label == expected


@pytest.mark.parametrize('value,expected', (
    ('COMPANIES_HOUSE', True),
    ('SOLE_TRADER', False),
))
def test_profile_parser_is_in_companies_house(value, expected):
    parser = helpers.CompanyParser({'company_type': value})

    assert parser.is_in_companies_house is expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_industries': 'thing'}, True),
    ({'expertise_regions': 'thing'}, True),
    ({'expertise_countries': 'thing'}, True),
    ({'expertise_languages': 'thing'}, True),
    ({'expertise_industries': ''}, False),
    ({'expertise_regions': ''}, False),
    ({'expertise_countries': ''}, False),
    ({'expertise_languages': ''}, False),
    ({}, False),
))
def test_profile_parser_has_expertise(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.has_expertise is expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_industries': ['MARINE']}, 'Marine'),
    ({'expertise_industries': ['MARINE', 'POWER']}, 'Marine, Power'),
    ({'expertise_industries': ['MARINE', '']}, 'Marine'),
    ({'expertise_industries': ['MARINE', None]}, 'Marine'),
    ({'expertise_industries': ['MARINE', 'bad-value']}, 'Marine'),
    ({'expertise_industries': []}, ''),
    ({'expertise_industries': ''}, ''),
    ({'expertise_industries': None}, ''),
    ({}, ''),
))
def test_profile_parser_expertise_industries_label(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.expertise_industries_label == expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_regions': ['LONDON']}, 'London'),
    ({'expertise_regions': ['LONDON', 'WALES']}, 'London, Wales'),
    ({'expertise_regions': ['LONDON', '']}, 'London'),
    ({'expertise_regions': ['LONDON', None]}, 'London'),
    ({'expertise_regions': ['LONDON', 'bad-value']}, 'London'),
    ({'expertise_regions': []}, ''),
    ({'expertise_regions': ''}, ''),
    ({'expertise_regions': None}, ''),
    ({}, ''),
))
def test_profile_parser_expertise_regions_label(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.expertise_regions_label == expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_countries': ['AL']}, 'Albania'),
    ({'expertise_countries': ['AL', 'AO']}, 'Albania, Angola'),
    ({'expertise_countries': ['AL', '']}, 'Albania'),
    ({'expertise_countries': ['AL', None]}, 'Albania'),
    ({'expertise_countries': ['AL', 'bad-value']}, 'Albania'),
    ({'expertise_countries': []}, ''),
    ({'expertise_countries': ''}, ''),
    ({'expertise_countries': None}, ''),
    ({}, ''),
))
def test_profile_parser_expertise_countries_label(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.expertise_countries_label == expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_languages': ['aa']}, 'Afar'),
    ({'expertise_languages': ['aa', 'ak']}, 'Afar, Akan'),
    ({'expertise_languages': ['aa', '']}, 'Afar'),
    ({'expertise_languages': ['aa', None]}, 'Afar'),
    ({'expertise_languages': ['aa', 'bad-value']}, 'Afar'),
    ({'expertise_languages': []}, ''),
    ({'expertise_languages': ''}, ''),
    ({'expertise_languages': None}, ''),
    ({}, ''),
))
def test_profile_parser_expertise_languages_label(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.expertise_languages_label == expected


@pytest.mark.parametrize('value,expected', (
    ({'expertise_products_services': {}}, {}),
    ({'expertise_products_services': ''}, {}),
    ({'expertise_products_services': None}, {}),
    ({}, {}),
    (
        {
            'expertise_products_services': {
                'publicity': [
                    'Public Relations',
                    'Branding',
                ],
                'further-services': [
                    'Business relocation',
                ]
            }
        },
        {
            'Publicity': 'Public Relations, Branding',
            'Further services': 'Business relocation',
        },
    ),
))
def test_profile_parser_expertise_products_services_label(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.expertise_products_services_label == expected


@pytest.mark.parametrize('value,expected', (
    ({'is_publishable': True}, True),
    ({'is_publishable': False}, False),
))
def test_profile_parser_is_publishable(value, expected):
    parser = helpers.CompanyParser(value)

    assert parser.is_publishable == expected


@pytest.mark.parametrize('value,expected', (
    ({}, False),
    ({'is_publishable': True}, True),
))
def test_profile_parser_(value, expected):
    parser = helpers.CompanyParser(value)

    assert bool(parser) is expected


@pytest.mark.parametrize('value,expected', (
    (
        'really good, nice, great and good',
        ['really good', 'nice', 'great and good'],
    ),
    (
        ' really good ,nice ,great and good ',
        ['really good', 'nice', 'great and good'],
    ),
    (
        'really good,nice,great and good',
        ['really good', 'nice', 'great and good'],

    ),
    (
        'really good,nice,great and good,',
        ['really good', 'nice', 'great and good'],
    ),
    (
        'really good,nice,great and good, ',
        ['really good', 'nice', 'great and good']
    )
))
def test_tokenize_keywords(value, expected):
    actual = helpers.tokenize_keywords(value)
    assert actual == expected


@pytest.mark.parametrize('url,expected', (
    ('/foo/bar/', '/foo/bar/?'),
    ('/foo/bar/?page=2', '/foo/bar/?'),
    ('/foo/bar/?page=2&baz=3', '/foo/bar/?baz=3&'),

))
def test_get_pagination_url(rf, url, expected):
    request = rf.get(url)
    assert helpers.get_pagination_url(request, 'page') == expected


def test_get_user_old(rf):
    sso_user = mock.Mock()
    request = rf.get('/')
    request.sso_user = sso_user
    assert helpers.get_user(request) == sso_user


def test_get_user_django_auth(rf):
    user = mock.Mock()
    request = rf.get('/')
    request.user = user
    assert helpers.get_user(request) == user


@pytest.mark.parametrize('user,expected', (
    (mock.Mock(spec=[]), True),
    (None, False)
))
def test_get_is_authenticated_old(user, expected, rf):
    request = rf.get('/')
    request.sso_user = user
    assert helpers.get_is_authenticated(request) is expected


@pytest.mark.parametrize('value', (True, False))
def test_get_is_authenticated_django_auth(value, rf):
    user = mock.Mock(spec=['is_authenticated'], is_authenticated=value)
    request = rf.get('/')
    request.user = user
    assert helpers.get_is_authenticated(request) == value
