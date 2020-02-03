from bs4 import BeautifulSoup
from directory_components.context_processors import urls_processor
import pytest

from django.template.loader import render_to_string

from tests.domestic import factories
from core.context_processors import signup_modal


def page_to_soup(page, request):
    context = {
        **page.get_context(request=request),
        **urls_processor(request),
        **signup_modal(request),
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
            var element = document.getElementById("header-sign-in-link")
            if (element) {
                ditMVP.UserStateModal({
                    element: element,
                    loginUrl: '/sso/api/business-login/',
                    signupUrl: '/sso/api/business-user-create/',
                    csrfToken: '123',
                    linkedInUrl: 'http://sso.trade.great:8004/sso/accounts/login/via-linkedin/?next=http://testserver/',
                    googleUrl: 'debug?next=http://testserver/',
                    termsUrl: 'https://www.great.gov.uk/terms-and-conditions/'
                })
            }
        </script>
    """, 'html.parser')

    assert soup_to_html(scripts[-1]) == soup_to_html(expected)
    assert soup.find(id='header-sign-in-link') is not None
