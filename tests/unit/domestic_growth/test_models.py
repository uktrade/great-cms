from wagtail.test.utils import WagtailPageTests

from tests.helpers import SetUpLocaleMixin
from .factories import DomesticGrowthHomePageFactory


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
