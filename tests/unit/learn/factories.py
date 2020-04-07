import factory.fuzzy
from wagtail_factories import PageFactory

from core import models


class TopicPageFactory(PageFactory):

    title = 'some topic'
    live = True
    slug = 'some-topic'
    template = 'learn/topic_page.html'

    class Meta:
        model = models.ListPage
        django_get_or_create = ['slug', 'parent']


class LessonPageFactory(PageFactory):

    title = 'some lesson'
    live = True
    slug = 'some-lesson'
    template = 'learn/lesson_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']
