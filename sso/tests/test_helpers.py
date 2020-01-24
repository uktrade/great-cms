from django.http import JsonResponse

from requests.cookies import RequestsCookieJar

from sso import helpers


def test_set_cookies_from_cookie_jar():
    response = JsonResponse(data={})

    cookie_jar = RequestsCookieJar()
    cookie_jar.set('foo', 'a secret value', domain='httpbin.org', path='/cookies')
    cookie_jar.set('bar', 'a secret value', domain='httpbin.org', path='/elsewhere')

    helpers.set_cookies_from_cookie_jar(
        cookie_jar=cookie_jar,
        response=response,
        whitelist=['bar']
    )

    assert 'foo' not in response.cookies
    assert 'bar' in response.cookies
    assert response.cookies['bar'].output() == (
        'Set-Cookie: bar="a secret value"; Domain=httpbin.org; HttpOnly; Path=/elsewhere'
    )