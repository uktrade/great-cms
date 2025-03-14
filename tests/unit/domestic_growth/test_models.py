from wagtail.test.utils import WagtailPageTests

from tests.helpers import SetUpLocaleMixin
from .factories import (
    DomesticGrowthHomePageFactory,
    DomesticGrowthGuidePageFactory,
    DomesticGrowthChildGuidePageFactory,
)
from domestic_growth.models import DomesticGrowthContent


class DomesticGrowthHomePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_homepage(self):
        homepage = DomesticGrowthHomePageFactory(
            hero_title='Test title',
            hero_intro='Test intro',
            guidance_title='Test title',
            about_title='Test title',
            about_intro='Test intro',
            about_description='Test description',
            news_title='Test title',
            news_link_url='www.test.com',
            news_link_text='Test link text',
            feedback_title='Test title',
            feedback_description='Test description',
            feedback_link_text='Test link text',
            feedback_link_url='Test link url',
        )
        self.assertEqual(homepage.title, 'homepage')

        self.assertEqual(homepage.hero_title, 'Test title')
        self.assertEqual(homepage.hero_intro, 'Test intro')
        self.assertEqual(homepage.guidance_title, 'Test title')
        self.assertEqual(homepage.about_title, 'Test title')
        self.assertEqual(homepage.about_intro, 'Test intro')
        self.assertEqual(homepage.about_description, 'Test description')
        self.assertEqual(homepage.news_title, 'Test title')
        self.assertEqual(homepage.news_link_url, 'www.test.com')
        self.assertEqual(homepage.news_link_text, 'Test link text')
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
        )
        self.assertEqual(page.title, 'guidepage')

        self.assertEqual(page.hero_title, 'Test title')
        self.assertEqual(page.hero_intro, 'Test intro')
        self.assertEqual(page.body_title, 'Test title')
        self.assertEqual(page.body_intro, 'Test intro')


class DomesticGrowthChildGuidePageTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_page(self):
        page = DomesticGrowthChildGuidePageFactory(
            body_title='Test title',
            body_intro='Test intro',
        )
        self.assertEqual(page.title, 'child-guidepage')

        self.assertEqual(page.body_title, 'Test title')
        self.assertEqual(page.body_intro, 'Test intro')


class DomesticGrowthContentTests(SetUpLocaleMixin, WagtailPageTests):
    def test_can_create_snippet(self):
        snippet = DomesticGrowthContent.objects.create(
            content_id='123', title='Test title', description='Test description', url='www.url.com'
        )

        self.assertEqual(snippet.content_id, '123')
        self.assertEqual(snippet.title, 'Test title')
        self.assertEqual(snippet.description, 'Test description')
        self.assertEqual(snippet.url, 'www.url.com')
