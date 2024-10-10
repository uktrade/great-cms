import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from core import constants, models
from learn.models import CsatUserFeedback
from tests.unit.core.factories import DetailPageFactory


class LessonPageFactory(DetailPageFactory):
    template = 'learn/detail_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']


class RelatedContentCTASnippetFactory(DjangoModelFactory):
    class Meta:
        model = models.RelatedContentCTA


class UKEACTASnippetFactory(DjangoModelFactory):
    class Meta:
        model = models.UKEACTA


class EventOrderableFactory(DjangoModelFactory):
    class Meta:
        model = models.EventOrderable


class HCSATFactory(factory.django.DjangoModelFactory):

    URL = factory.fuzzy.FuzzyText(length=100)
    user_journey = factory.fuzzy.FuzzyChoice(constants.USER_JOURNEY_CHOICES, getter=lambda choice: choice[0])
    satisfaction_rating = factory.fuzzy.FuzzyChoice(constants.SATISFACTION_CHOICES, getter=lambda choice: choice[0])
    experienced_issues = [factory.fuzzy.FuzzyChoice(constants.EXPERIENCE_CHOICES, getter=lambda choice: choice[0])]
    other_detail = factory.fuzzy.FuzzyText(length=255)
    service_improvements_feedback = factory.fuzzy.FuzzyText(length=255)
    likelihood_of_return = factory.fuzzy.FuzzyChoice(constants.LIKELIHOOD_CHOICES, getter=lambda choice: choice[0])

    class Meta:
        model = CsatUserFeedback
