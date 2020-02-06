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


def remove_whitespace(html):
    return html.replace('\n', '').replace('  ', '').strip()


@pytest.mark.django_db
def test_domestic_home_template_contains_login_javascript(client, rf):
    page = factories.DomesticHomePageFactory()
    soup = page_to_soup(page=page, request=rf.get('/'))

    cofig_js = """
        ditMVP.setConfig({
            loginUrl: '/sso/api/business-login/',
            signupUrl: '/sso/api/business-user-create/',
            verifyCodeUrl: '/sso/api/business-verify-code/',
            csrfToken: '123',
            linkedInUrl: 'http://sso.trade.great:8004/sso/accounts/login/via-linkedin/?next=http://testserver/',
            googleUrl: 'debug?next=http://testserver/',
            termsUrl: 'https://www.great.gov.uk/terms-and-conditions/'
        })
    """
    modal_js = """
        ditMVP.SignupModal({
            element: element.parentElement,
            currentStep: step,
            isOpen: isOpen,
            username: username
        })
    """

    assert remove_whitespace(cofig_js) in remove_whitespace(soup.text)
    assert remove_whitespace(modal_js) in remove_whitespace(soup.text)
    assert soup.find(id='header-sign-in-link') is not None
