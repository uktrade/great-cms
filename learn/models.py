from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.core.models import Page, Orderable

from django.db import models


class TopicPage(Page):

    description = models.TextField()

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        InlinePanel('lessons', label='Lessons'),
    ]


class LessonPage(Orderable):

    description = models.TextField()
    page = ParentalKey(TopicPage, on_delete=models.CASCADE, related_name='lessons')

    panels = [
        FieldPanel('description'),
    ]
