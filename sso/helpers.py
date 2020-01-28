def set_cookies_from_cookie_jar(cookie_jar, response, whitelist):
    for cookie in cookie_jar:
        if cookie.name in whitelist:
            response.set_cookie(
                cookie.name,
                cookie.value,
                expires=cookie.expires,
                path=cookie.path,
                secure=cookie.secure,
                domain=cookie.domain,
                httponly=cookie.has_nonstandard_attr('HttpOnly'),
            )
