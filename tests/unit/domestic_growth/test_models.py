from unittest import mock
from unittest.mock import patch

import pytest
from django.test.client import RequestFactory
from elasticsearch.exceptions import TransportError
from rest_framework import status
from wagtail.test.utils import WagtailPageTests
from wagtail_factories import SiteFactory

from config.settings import DOMESTIC_GROWTH_EMAIL_GUIDE_TEMPLATE_ID
from core.fern import Fern
from domestic_growth.models import (
    DomesticGrowthCard,
    DomesticGrowthContent,
    ExistingBusinessTriage,
)
from tests.helpers import SetUpLocaleMixin
from .factories import (
    DomesticGrowthChildGuidePageFactory,
    DomesticGrowthDynamicChildGuidePageFactory,
    DomesticGrowthGuidePageFactory,
    DomesticGrowthHomePageFactory,
)


class DomesticGrowthHomePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_homepage(self):
        homepage = DomesticGrowthHomePageFactory(
            hero_title='Test title',
            hero_intro='Test intro',
            case_study_title='Test title',
            case_study_intro='Test intro',
            case_study_link_text='Test link text',
            case_study_link_url='Test link url',
            guidance_title='Test title',
            news_title='Test title',
            news_link_url='www.test.com',
            news_link_text='Test link text',
            news_link_text_extra='Test link text extra',
            news_link_url_extra='www.testextra.com',
            feedback_title='Test title',
            feedback_description='Test description',
            feedback_link_text='Test link text',
            feedback_link_url='Test link url',
        )
        self.assertEqual(homepage.title, 'homepage')

        self.assertEqual(homepage.hero_title, 'Test title')
        self.assertEqual(homepage.hero_intro, 'Test intro')
        self.assertEqual(homepage.case_study_title, 'Test title')
        self.assertEqual(homepage.case_study_intro, 'Test intro')
        self.assertEqual(homepage.case_study_link_text, 'Test link text')
        self.assertEqual(homepage.case_study_link_url, 'Test link url')
        self.assertEqual(homepage.guidance_title, 'Test title')
        self.assertEqual(homepage.news_title, 'Test title')
        self.assertEqual(homepage.news_link_url, 'www.test.com')
        self.assertEqual(homepage.news_link_text, 'Test link text')
        self.assertEqual(homepage.news_link_url, 'www.test.com')
        self.assertEqual(homepage.news_link_text_extra, 'Test link text extra')
        self.assertEqual(homepage.news_link_url_extra, 'www.testextra.com')
        self.assertEqual(homepage.feedback_title, 'Test title')
        self.assertEqual(homepage.feedback_description, 'Test description')
        self.assertEqual(homepage.feedback_link_text, 'Test link text')
        self.assertEqual(homepage.feedback_link_url, 'Test link url')


class DomesticGrowthGuidePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_page(self):
        page = DomesticGrowthGuidePageFactory(
            hero_title='Test title',
            hero_intro='Test intro',
            body_title='Test title',
            body_intro='Test intro',
            primary_regional_support_title_england='Test title',
            primary_regional_support_intro_england='Test intro',
            primary_regional_support_title_scotland='Test title',
            primary_regional_support_intro_scotland='Test intro',
            primary_regional_support_title_ni='Test title',
            primary_regional_support_intro_ni='Test intro',
            primary_regional_support_title_wales='Test title',
            primary_regional_support_intro_wales='Test intro',
            chamber_of_commerce_intro='Test intro',
            trade_associations_title='Test title',
            trade_associations_intro='Test intro',
        )
        self.assertEqual(page.title, 'guidepage')

        self.assertEqual(page.hero_title, 'Test title')
        self.assertEqual(page.hero_intro, 'Test intro')
        self.assertEqual(page.body_title, 'Test title')
        self.assertEqual(page.body_intro, 'Test intro')
        self.assertEqual(page.primary_regional_support_title_england, 'Test title')
        self.assertEqual(page.primary_regional_support_intro_england, 'Test intro')
        self.assertEqual(page.primary_regional_support_title_scotland, 'Test title')
        self.assertEqual(page.primary_regional_support_intro_scotland, 'Test intro')
        self.assertEqual(page.primary_regional_support_title_ni, 'Test title')
        self.assertEqual(page.primary_regional_support_intro_ni, 'Test intro')
        self.assertEqual(page.primary_regional_support_title_wales, 'Test title')
        self.assertEqual(page.primary_regional_support_intro_wales, 'Test intro')
        self.assertEqual(page.chamber_of_commerce_intro, 'Test intro')
        self.assertEqual(page.trade_associations_title, 'Test title')
        self.assertEqual(page.trade_associations_intro, 'Test intro')

    def test_can_email_guide(self):
        with patch('domestic_growth.models.actions.GovNotifyEmailAction') as mock_gov_uk_notify_action, patch(
            'domestic_growth.models.token_urlsafe'
        ) as mock_token_urlsafe:
            try:
                page = DomesticGrowthGuidePageFactory(
                    hero_title='Test title',
                    hero_intro='Test intro',
                    body_title='Test title',
                    body_intro='Test intro',
                    primary_regional_support_title_england='Test title',
                    primary_regional_support_intro_england='Test intro',
                    primary_regional_support_title_scotland='Test title',
                    primary_regional_support_intro_scotland='Test intro',
                    primary_regional_support_title_ni='Test title',
                    primary_regional_support_intro_ni='Test intro',
                    primary_regional_support_title_wales='Test title',
                    primary_regional_support_intro_wales='Test intro',
                    chamber_of_commerce_intro='Test intro',
                    trade_associations_title='Test title',
                    trade_associations_intro='Test intro',
                    slug='test-email-guide',
                )
            except TransportError:
                # Page is created at this point. Error caused by being unable to add page to Opensearch index.
                pass

            factory = RequestFactory()
            test_email = 'test@example.com'  # /PS-IGNORE
            terms_agreed = True
            test_triage_uuid = '12345'
            mock_token_urlsafe.return_value = 'urltokensafestring'
            encrypted_test_triage_uuid = Fern().encrypt(test_triage_uuid)

            ExistingBusinessTriage.objects.create(triage_uuid=test_triage_uuid)

            req = factory.post(
                f'/test-email-guide?triage_uuid={encrypted_test_triage_uuid}',
                {'email': test_email, 'terms_agreed': terms_agreed},
            )
            response = page.serve(req)

            assert response.status_code is status.HTTP_200_OK

            mock_gov_uk_notify_action.assert_called_once_with(
                email_address=test_email,
                template_id=DOMESTIC_GROWTH_EMAIL_GUIDE_TEMPLATE_ID,
                form_url='http://testserver/test-email-guide?url_token=urltokensafestring',
            )


class DomesticGrowthChildGuidePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_page(self):
        page = DomesticGrowthChildGuidePageFactory(
            body_title='Test title',
            body_intro='Test intro',
        )
        self.assertEqual(page.title, 'child-guidepage')

        self.assertEqual(page.body_title, 'Test title')
        self.assertEqual(page.body_intro, 'Test intro')

    def test_can_email_guide(self):
        with patch('domestic_growth.models.actions.GovNotifyEmailAction') as mock_gov_uk_notify_action, patch(
            'domestic_growth.models.token_urlsafe'
        ) as mock_token_urlsafe:
            try:
                page = DomesticGrowthChildGuidePageFactory(
                    body_title='Test title',
                    body_intro='Test intro',
                    slug='test-email-guide',
                )
            except TransportError:
                # Page is created at this point. Error caused by being unable to add page to Opensearch index.
                pass

            factory = RequestFactory()
            test_email = 'test@example.com'  # /PS-IGNORE
            terms_agreed = True
            test_triage_uuid = '12345'
            mock_token_urlsafe.return_value = 'urltokensafestring'
            encrypted_test_triage_uuid = Fern().encrypt(test_triage_uuid)

            ExistingBusinessTriage.objects.create(triage_uuid=test_triage_uuid)

            req = factory.post(
                f'/test-email-guide?triage_uuid={encrypted_test_triage_uuid}',
                {'email': test_email, 'terms_agreed': terms_agreed},
            )
            response = page.serve(req)

            assert response.status_code is status.HTTP_200_OK

            mock_gov_uk_notify_action.assert_called_once_with(
                email_address=test_email,  # /PS-IGNORE
                template_id=DOMESTIC_GROWTH_EMAIL_GUIDE_TEMPLATE_ID,
                form_url='http://testserver/test-email-guide?url_token=urltokensafestring',
            )


class DomesticGrowthDynamicChildGuidePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_page(self):
        page = DomesticGrowthDynamicChildGuidePageFactory(
            page_a_type='interested_in_exporting',
            page_a_body_title='Test title a',
            page_a_body_intro='Test intro a',
            page_b_type='not_interested_in_exporting',
            page_b_body_title='Test title b',
            page_b_body_intro='Test intro b',
        )
        self.assertEqual(page.title, 'dynamic-child-guidepage')

        self.assertEqual(page.page_a_type, 'interested_in_exporting')
        self.assertEqual(page.page_a_body_title, 'Test title a')
        self.assertEqual(page.page_a_body_intro, 'Test intro a')
        self.assertEqual(page.page_b_type, 'not_interested_in_exporting')
        self.assertEqual(page.page_b_body_title, 'Test title b')
        self.assertEqual(page.page_b_body_intro, 'Test intro b')

    def test_can_email_guide(self):
        with patch('domestic_growth.models.actions.GovNotifyEmailAction') as mock_gov_uk_notify_action, patch(
            'domestic_growth.models.token_urlsafe'
        ) as mock_token_urlsafe:
            try:
                page = DomesticGrowthDynamicChildGuidePageFactory(
                    page_a_type='interested_in_exporting',
                    page_a_body_title='Test title a',
                    page_a_body_intro='Test intro a',
                    page_b_type='not_interested_in_exporting',
                    page_b_body_title='Test title b',
                    page_b_body_intro='Test intro b',
                    slug='test-email-guide',
                )
            except TransportError:
                # Page is created at this point. Error caused by being unable to add page to Opensearch index.
                pass

            factory = RequestFactory()
            test_email = 'test@example.com'  # /PS-IGNORE
            terms_agreed = True
            test_triage_uuid = '12345'
            mock_token_urlsafe.return_value = 'urltokensafestring'

            encrypted_test_triage_uuid = Fern().encrypt(test_triage_uuid)
            ExistingBusinessTriage.objects.create(triage_uuid=test_triage_uuid)

            req = factory.post(
                f'/test-email-guide?triage_uuid={encrypted_test_triage_uuid}',
                {'email': test_email, 'terms_agreed': terms_agreed},
            )
            response = page.serve(req)

            assert response.status_code is status.HTTP_200_OK

            mock_gov_uk_notify_action.assert_called_once_with(
                email_address=test_email,  # /PS-IGNORE
                template_id=DOMESTIC_GROWTH_EMAIL_GUIDE_TEMPLATE_ID,
                form_url='http://testserver/test-email-guide?url_token=urltokensafestring',
            )


class DomesticGrowthContentTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_snippet(self):
        snippet = DomesticGrowthContent.objects.create(
            content_id='123',
            title='Test title',
            description='Test description',
            url='www.url.com',
            region='London',
            sector='Aerospace',
            sub_sector='Manufacturing and assembly',
            is_dynamic=False,
            show_image=False,
        )

        self.assertEqual(snippet.content_id, '123')
        self.assertEqual(snippet.title, 'Test title')
        self.assertEqual(snippet.description, 'Test description')
        self.assertEqual(snippet.url, 'www.url.com')
        self.assertEqual(snippet.region, 'London')
        self.assertEqual(snippet.sector, 'Aerospace')
        self.assertEqual(snippet.sub_sector, 'Manufacturing and assembly')
        self.assertEqual(snippet.is_dynamic, False)
        self.assertEqual(snippet.show_image, False)


class DomesticGrowthCardTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_snippet(self):
        snippet = DomesticGrowthCard.objects.create(
            title='Test title', description='Test description', url='www.url.com', meta_text='Test meta text'
        )

        self.assertEqual(snippet.title, 'Test title')
        self.assertEqual(snippet.description, 'Test description')
        self.assertEqual(snippet.url, 'www.url.com')
        self.assertEqual(snippet.meta_text, 'Test meta text')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'ip,expected_target_lang',
    (
        ('221.194.47.204, 127.0.0.1, 127.0.0.2', 'zh-hans'),
        ('144.76.204.44, 127.0.0.1, 127.0.0.2', 'de'),
        ('195.12.50.155, 127.0.0.1, 127.0.0.2', 'es'),
        ('110.50.243.6, 127.0.0.1, 127.0.0.2', 'ja'),
        ('86.144.101.167, 127.0.0.1, 127.0.0.2', None),
    ),
)
@mock.patch(('domestic_growth.helpers.get_dbt_news_articles'))
def test_domestic_growth_homepage_geo_redirect__integration(
    mock_get_dbt_news_articles,
    root_page,
    client,
    ip,
    expected_target_lang,
):
    mock_get_dbt_news_articles.return_value = []
    homepage = DomesticGrowthHomePageFactory(
        parent=root_page,
        slug='root',
        hero_title='Test title',
        hero_intro='Test intro',
        case_study_title='Test case study',
        case_study_intro='Test case study intro',
        case_study_link_text='Test case study link text',
        case_study_link_url='Test case study link url',
        guidance_title='Test guidance title',
        news_title='Test news title',
        news_link_text='Test link text',
        news_link_url='Test link url',
        news_link_text_extra='Test news link text extra',
        news_link_url_extra='Test news link url extra',
        feedback_title='Test feedback title',
        feedback_description='Test feedback description',
        feedback_link_text='Test feedback link text',
        feedback_link_url='Test feedback link url',
    )

    SiteFactory(
        root_page=homepage,
        hostname=client._base_environ()['SERVER_NAME'],
    )

    response = client.get(homepage.url, HTTP_X_FORWARDED_FOR=ip)

    if expected_target_lang is not None:
        assert response.status_code == 302
        assert response.headers['Location'] == f'/invest-in-uk/?lang={expected_target_lang}'
    else:
        assert response.status_code == 200
