import factory.fuzzy
import wagtail_factories

from learn import models


class TopicPageFactory(wagtail_factories.PageFactory):

    title = 'some topic'
    live = True
    slug = 'some-topic'
    description = factory.fuzzy.FuzzyText(length=200)

    class Meta:
        model = models.TopicPage
        django_get_or_create = ['slug', 'parent']


class LessonPageFactory(wagtail_factories.PageFactory):

    title = 'some lesson'
    live = True
    slug = 'some-lesson'
    generic_content = factory.fuzzy.FuzzyText(length=200)

    class Meta:
        model = models.LessonPage
        django_get_or_create = ['slug', 'parent']
