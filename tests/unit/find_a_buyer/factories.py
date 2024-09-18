import factory
import factory.fuzzy
from find_a_buyer import choices
from find_a_buyer.models import CsatUserFeedback

class HCSATFactory(factory.django.DjangoModelFactory):

    URL = factory.fuzzy.FuzzyText(length=100)
    user_journey = factory.fuzzy.FuzzyChoice(choices.USER_JOURNEY_CHOICES, getter=lambda choice: choice[0])
    satisfaction_rating = factory.fuzzy.FuzzyChoice(choices.SATISFACTION_CHOICES, getter=lambda choice: choice[0])
    experienced_issues = factory.fuzzy.FuzzyChoice(choices.EXPERIENCE_CHOICES, getter=lambda choice: choice[0])
    other_detail = factory.fuzzy.FuzzyText(length=255)
    service_improvements_feedback = factory.fuzzy.FuzzyText(length=255)
    likelihood_of_return = factory.fuzzy.FuzzyChoice(choices.LIKELIHOOD_CHOICES, getter=lambda choice: choice[0])

    class Meta:
        model = CsatUserFeedback
