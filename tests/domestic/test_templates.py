import pytest

from django.template.loader import render_to_string

from tests.domestic import factories

from directory_components.context_processors import urls_processor
from bs4 import BeautifulSoup


def page_to_soup(page, request):
    context = {
        **page.get_context(request=request),
        **urls_processor(request),
        'csrf_token': '123',
    }
    html = render_to_string(page.get_template(request=request), context=context)
    return BeautifulSoup(html, 'html.parser')


def soup_to_html(soup):
    return soup.text.replace('\n', '').replace('  ', '').strip()


@pytest.mark.django_db
def test_domestic_home_template_contains_login_javascript(client, rf):
    page = factories.DomesticHomePageFactory()
    soup = page_to_soup(page=page, request=rf.get('/'))

    scripts = soup.find_all('script')

    expected = BeautifulSoup("""
        <script type="text/javascript">
            var loginLink = document.getElementById("header-sign-in-link")
            if (loginLink) {
                ditMVP.LoginModal({
                    element: loginLink,
                    loginUrl: '/sso/api/business-login/',
                    csrfToken: '123'
                });
            }
        </script>
    """, 'html.parser')

    assert soup_to_html(scripts[-1]) == soup_to_html(expected)
    assert soup.find(id='header-sign-in-link') is not None
