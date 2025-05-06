import json
from unittest import mock

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse, reverse_lazy
from django.utils.translation import activate
from wagtail.models import Locale, Site
from wagtail.test.utils import WagtailPageTests

import domestic.forms
import domestic.views.campaign
import domestic.views.ukef
from core import cms_slugs
from core.constants import CONSENT_EMAIL
from domestic import forms
from domestic.views.ukef import GetFinanceLeadGenerationFormView
from tests.unit.core.factories import StructurePageFactory
from tests.unit.domestic.factories import ArticleListingPageFactory, ArticlePageFactory

pytestmark = [
    pytest.mark.django_db,
]


def test_landing_page_not_logged_in(client, user, domestic_site):
    response = client.get('/')
    assert response.status_code == 200


def test_landing_page_logged_in(client, user, domestic_site):
    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 302
    assert response.url == cms_slugs.DASHBOARD_URL


@pytest.mark.skipif(settings.FEATURE_DEA_V2, reason='Redirect to external pages')
@pytest.mark.parametrize(
    'page_url,page_content,expected_status_code',
    (
        (
            reverse('domestic:get-finance'),
            {
                'title': 'UK Export Finance',
            },
            200,
        ),
        (
            reverse('domestic:project-finance'),
            {
                'title': 'UK Export Finance - Project Finance',
            },
            200,
        ),
        (
            reverse('domestic:uk-export-contact'),
            {
                'title': 'UK Export Finance - Get in touch',
            },
            200,
        ),
        (
            reverse('domestic:how-we-assess-your-project'),
            {
                'title': 'UK Export Finance - How we assess your project',
            },
            200,
        ),
        (
            reverse('domestic:what-we-offer-you'),
            {
                'title': 'UK Export Finance - What we offer you',
            },
            200,
        ),
        (
            reverse('domestic:country-cover'),
            {
                'title': 'UK Export Finance - Check our Country Cover',
            },
            200,
        ),
    ),
)
def test_ukef_views(client, page_url, page_content, expected_status_code):
    response = client.get(page_url)
    assert response.status_code == expected_status_code
    if len(page_content) > 0:
        assert page_content['title'] in str(response.rendered_content)


@mock.patch.object(domestic.views.ukef.ContactView, 'form_session_class')
@mock.patch.object(domestic.forms.UKEFContactForm, 'save')
def test_ukef_contact_form_notify_success(
    mock_save,
    mock_form_session,
    client,
    valid_contact_form_data,
):
    url = reverse('domestic:uk-export-contact')
    response = client.post(url, valid_contact_form_data)
    assert response.status_code == 302
    assert response.url == reverse('domestic:uk-export-contact-success')
    assert mock_save.call_count == 2
    assert mock_save.call_args_list == [
        mock.call(
            email_address=settings.UKEF_CONTACT_AGENT_EMAIL_ADDRESS,
            form_session=mock_form_session(),
            form_url=url,
            sender={
                'email_address': 'test@test.com',  # /PS-IGNORE
                'country_code': None,
                'ip_address': None,
            },
            template_id=settings.UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID,
        ),
        mock.call(
            email_address='test@test.com',  # /PS-IGNORE
            form_session=mock_form_session(),
            form_url=url,
            template_id=settings.UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID,
        ),
    ]


def test_ukef_contact_form_success_view_response(rf):
    user_email = 'test@test.com'  # /PS-IGNORE
    request = rf.get(reverse('domestic:uk-export-contact-success'))
    request.user = AnonymousUser()
    request.session = {'user_email': user_email}  # /PS-IGNORE
    view = domestic.views.ukef.SuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 200
    assert user_email in response.rendered_content

    # test page redirect if the email doesn't exists in the session
    request.session = {}
    view = domestic.views.ukef.SuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 302


@pytest.mark.skipif(settings.FEATURE_DEA_V2, reason='Redirect to external pages')
def test_ukef_get_finance_card_bullets(client):
    url = reverse('domestic:get-finance')
    response = client.get(url)
    trade_finance_bullets = [
        'working capital support',
        'bond support',
        'credit insurance',
    ]
    project_finance_bullets = [
        'UKEF buyer credit guarantees',
        'direct lending',
        'credit and bond insurance',
    ]

    for bullet in trade_finance_bullets:
        assert f'<li>{bullet}</li>' in str(response.content)

    for bullet in project_finance_bullets:
        assert f'<li>{bullet}</li>' in str(response.content)


@pytest.mark.parametrize('step', ('your-details', 'company-details', 'help'))
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ukef_lead_generation(client, step):
    url = reverse(
        'domestic:uk-export-finance-lead-generation-form',
        kwargs={'step': step},
    )
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [
        GetFinanceLeadGenerationFormView.templates[step],
    ]


@mock.patch('captcha.fields.ReCaptchaField.clean')
@mock.patch('domestic.views.ukef.PardotAction')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ukef_lead_generation_captcha_revalidation(
    mock_action,
    mock_clean,
    client,
    captcha_stub,
):
    url_name = 'domestic:uk-export-finance-lead-generation-form'
    view_name = 'get_finance_lead_generation_form_view'

    response = client.post(
        reverse(url_name, kwargs={'step': 'your-details'}),
        {
            view_name + '-current_step': 'your-details',
            'your-details-firstname': 'test',  # /PS-IGNORE
            'your-details-lastname': 'test',  # /PS-IGNORE
            'your-details-position': 'test',
            'your-details-email': 'test@example.com',  # /PS-IGNORE
            'your-details-phone': 'test',
        },
    )
    assert response.status_code == 302

    response = client.post(
        reverse(url_name, kwargs={'step': 'company-details'}),
        {
            view_name + '-current_step': 'company-details',
            'company-details-trading_name': 'test',
            'company-details-company_number': 'test',
            'company-details-address_line_one': 'test',
            'company-details-address_line_two': 'test',
            'company-details-address_town_city': 'test',
            'company-details-address_county': 'test',
            'company-details-address_post_code': 'test',
            'company-details-industry': 'Other',
            'company-details-industry_other': 'test',
            'company-details-export_status': 'I have customers outside UK',
        },
    )
    assert response.status_code == 302

    response = client.post(
        reverse(url_name, kwargs={'step': 'help'}),
        {
            view_name + '-current_step': 'help',
            'help-comment': 'test',
            'help-contact_consent': [CONSENT_EMAIL],
            'g-recaptcha-response': captcha_stub,
        },
    )

    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse(
        'domestic:uk-export-finance-lead-generation-form-success',
    )
    assert mock_clean.call_count == 1


@mock.patch('domestic.views.ukef.PardotAction')
def test_ukef_lead_generation_submit(mock_action, client, settings, captcha_stub):
    settings.UKEF_FORM_SUBMIT_TRACKER_URL = 'submit.com'

    view = GetFinanceLeadGenerationFormView()

    form_one = forms.CategoryForm(data={'categories': ['Securing upfront funding']})
    form_two = forms.HelpForm(
        data={
            'comment': 'thing',
            'contact_consent': [CONSENT_EMAIL],
            'g-recaptcha-response': captcha_stub,
        }
    )
    form_three = forms.PersonalDetailsForm(
        data={
            'firstname': 'Test',  # /PS-IGNORE
            'lastname': 'Example',  # /PS-IGNORE
            'position': 'Thing',
            'email': 'test@example.com',  # /PS-IGNORE
            'phone': '2342',
        }
    )

    assert form_one.is_valid()
    assert form_two.is_valid()
    assert form_three.is_valid()

    response = view.done([form_one, form_two, form_three])

    assert response.status_code == 302
    assert response.url == str(view.success_url)

    assert mock_action.call_count == 1
    assert mock_action.call_args == mock.call(
        pardot_url=settings.UKEF_FORM_SUBMIT_TRACKER_URL,
        form_url=reverse(
            'domestic:uk-export-finance-lead-generation-form',
            kwargs={'step': 'your-details'},
        ),
        sender={
            'email_address': 'test@example.com',  # /PS-IGNORE
            'country_code': None,
            'ip_address': None,
        },
    )

    assert mock_action().save.call_count == 1
    assert mock_action().save.call_args == mock.call(
        {
            'categories': ['Securing upfront funding'],
            'comment': 'thing',
            'captcha': 'PASS',
            'firstname': 'Test',  # /PS-IGNORE
            'lastname': 'Example',  # /PS-IGNORE
            'position': 'Thing',
            'email': 'test@example.com',  # /PS-IGNORE
            'phone': '2342',
            'contact_consent': [CONSENT_EMAIL],
        }
    )


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ukef_lead_generation_success_page(client):
    url = reverse('domestic:uk-export-finance-lead-generation-form-success')
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [
        'domestic/finance/lead_generation_form/success.html',
    ]


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ukef_lead_generation_initial_data(client, user, mock_get_company_profile):
    mock_get_company_profile.return_value = {
        # Full spec of CompanySerializer is in
        # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
        'name': 'Example corp',
        'number': 1234567,
        'mobile_number': '07171771717',
        'sectors': ['AEROSPACE', 'OTHER SECTOR THAT WILL NOT BE USED'],
        'address_line_1': '123 Street',
        'address_line_2': 'Near Fake Town',
        'locality': 'Paris',
        'postal_code': 'Foo Bar',
    }

    url_name = 'domestic:uk-export-finance-lead-generation-form'

    client.force_login(user)

    response_one = client.get(reverse(url_name, kwargs={'step': 'your-details'}))

    assert response_one.context_data['form'].initial == {
        'email': user.email,  # /PS-IGNORE
        'phone': '07171771717',
        'firstname': 'Jim',  # /PS-IGNORE
        'lastname': 'Cross',  # /PS-IGNORE
    }

    response_two = client.get(reverse(url_name, kwargs={'step': 'company-details'}))

    assert response_two.context_data['form'].initial == {
        'not_companies_house': False,
        'company_number': 1234567,
        'trading_name': 'Example corp',
        'industry': 'AEROSPACE',
        'address_line_one': '123 Street',
        'address_line_two': 'Near Fake Town',
        'address_town_city': 'Paris',
        'address_post_code': 'Foo Bar',
    }


class CampaignViewTestCase(WagtailPageTests, TestCase):
    @pytest.fixture(autouse=True)
    def domestic_homepage_fixture(self, domestic_homepage):
        self.domestic_homepage = domestic_homepage

    def setUp(self):
        self.parent_page = StructurePageFactory(parent=self.domestic_homepage, title='campaigns', slug='campaigns')
        self.fr_locale = Locale.objects.get_or_create(language_code='fr')
        article_body1 = json.dumps(
            [
                {
                    'type': 'form',
                    'value': {
                        'type': 'Short',
                        'email_title': 'title1',
                        'email_subject': 'subject1',
                        'email_body': 'body1',
                    },
                }
            ]
        )

        article_body2 = json.dumps([])

        article_body3 = json.dumps(
            [
                {
                    'type': 'form',
                    'value': {
                        'type': 'Long',
                        'email_title': 'title1',
                        'email_subject': 'subject1',
                        'email_body': 'body1',
                    },
                }
            ]
        )

        self.article1 = ArticlePageFactory(
            slug='test-article-one', article_body=article_body1, parent=self.parent_page, article_title='test'
        )

        self.article2 = ArticlePageFactory(
            slug='test-article-two', article_body=article_body2, parent=self.parent_page, article_title='test'
        )

        self.article3 = ArticlePageFactory(
            slug='test-article-three', article_body=article_body3, parent=self.parent_page, article_title='test'
        )

        self.site = Site.objects.create(hostname='greatcms.trade.great', root_page=self.domestic_homepage, site_name='Great', is_default_site=True) # noqa

    def test_no_page_slug(self):
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': None})
        request = self.client.get(url)
        self.assertEqual(request.status_code, 404)

    def test_page_does_not_exist(self):
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': 'page_that_does_not_exist'})
        request = self.client.get(url)
        self.assertEqual(request.status_code, 404)

    def test_get_current_page(self):
        self.listing_page = ArticleListingPageFactory(
            slug='test-listing', title='test', landing_page_title='test', hero_teaser='list one', parent = self.domestic_homepage) # noqa

        self.article = ArticlePageFactory(slug='test-article-one', parent=self.listing_page, article_title='test')

        factory = RequestFactory()
        url = '/campaigns/test-article-one/'
        request = factory.get(url)
        view = domestic.views.campaign.CampaignView()
        view.setup(request, page_slug='test-article-one')
        self.assertEqual(view.path, url)
        self.assertIsNotNone(view.current_page)

    def test_get_languages_with_only_one_language(self):
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': 'test-article-one'})
        request = self.client.get(url)
        view = domestic.views.campaign.CampaignView(request=request)
        current_page = view.request.context_data['view']
        self.assertEqual(current_page.current_language, 'en-gb')
        self.assertEqual([language['language_code'] for language in current_page.available_languages], ['en-gb'])

    def test_get_language_with_two_or_more_languages(self):
        site_fr = self.article1.copy_for_translation(self.fr_locale[0], copy_parents=True, alias=True)
        site_fr.save()
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': 'test-article-one'}) + '?lang=fr'
        request = self.client.get(url)
        view = domestic.views.campaign.CampaignView(request=request)
        current_page = view.request.context_data['view']
        self.assertEqual(current_page.current_language, 'fr')
        self.assertEqual(
            [language['language_code'] for language in current_page.available_languages],
            ['en-gb', 'fr'],
        )

    def test_get_language_default_value(self):
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': 'test-article-one'})
        request = self.client.get(url)
        view = domestic.views.campaign.CampaignView(request=request)
        current_page = view.request.context_data['view']
        self.assertEqual(current_page.current_language, 'en-gb')
        self.assertEqual([language['language_code'] for language in current_page.available_languages], ['en-gb'])

    def test_lang_not_in_locale_doesnt_break_and_uses_default_lang_instead(self):
        activate('abc')
        url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': 'test-article-one'})
        request = self.client.get(url)
        self.assertEqual(request.status_code, 200)
        view = domestic.views.campaign.CampaignView(request=request)
        current_page = view.request.context_data['view']
        self.assertEqual(current_page.current_language, 'en-gb')
        activate(None)
