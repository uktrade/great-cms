from django.contrib.postgres.fields import ArrayField
from django.db import models

from core import constants
from core.models import TimeStampedModel


class CsatUserFeedback(TimeStampedModel):
    URL = models.CharField(max_length=255)
    user_journey = models.CharField(
        max_length=255, null=True, choices=constants.USER_JOURNEY_CHOICES_LEARN, default='ARTICLE_PAGE'
    )
    satisfaction_rating = models.CharField(max_length=255, choices=constants.SATISFACTION_CHOICES)
    experienced_issues = ArrayField(
        models.CharField(max_length=255, choices=constants.EXPERIENCE_CHOICES), size=6, default=list, null=True
    )
    other_detail = models.CharField(max_length=255, null=True)
    service_improvements_feedback = models.CharField(max_length=3000, null=True)
    likelihood_of_return = models.CharField(max_length=255, choices=constants.LIKELIHOOD_CHOICES, null=True)
