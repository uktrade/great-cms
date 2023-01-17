from django.db import models
from wagtail.admin.edit_handlers import FieldPanel

from core.models import TimeStampedModel


class Event(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    url = models.CharField(null=True, blank=True, max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    live = models.BooleanField(default=False)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('url'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('live'),
    ]
