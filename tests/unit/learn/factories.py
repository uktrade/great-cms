from factory.django import DjangoModelFactory

from core import models
from tests.unit.core.factories import DetailPageFactory


class LessonPageFactory(DetailPageFactory):
    template = 'learn/detail_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']


class RelatedContentCTASnippetFactory(DjangoModelFactory):
    class Meta:
        model = models.RelatedContentCTA
