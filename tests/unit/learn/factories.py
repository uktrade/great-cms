import factory.fuzzy
from wagtail_factories import PageFactory

from learn import models


class TopicPageFactory(PageFactory):

    title = 'some topic'
    live = True
    slug = 'some-topic'
    description = factory.fuzzy.FuzzyText(length=200)

    class Meta:
        model = models.TopicPage
        django_get_or_create = ['slug', 'parent']


class LessonPageFactory(PageFactory):

    title = 'some lesson'
    live = True
    slug = 'some-lesson'
    generic_content = factory.fuzzy.FuzzyText(length=200)

    class Meta:
        model = models.LessonPage
        django_get_or_create = ['slug', 'parent']


class LearnPageFactory(PageFactory):
    title = 'learn page'
    live = True

    class Meta:
        model = models.LearnPage
        django_get_or_create = ['slug', 'parent']
