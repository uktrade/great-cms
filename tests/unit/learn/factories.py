from core import models
from tests.unit.core.factories import ListPageFactory, DetailPageFactory


class TopicPageFactory(ListPageFactory):

    template = 'learn/topic_page.html'
    record_read_progress = True

    class Meta:
        model = models.ListPage
        django_get_or_create = ['slug', 'parent']


class LessonPageFactory(DetailPageFactory):
    template = 'learn/lesson_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']
