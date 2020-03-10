from django.core.exceptions import ObjectDoesNotExist
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail_personalisation.blocks import PersonalisedStructBlock

from wagtail_personalisation.models import PersonalisablePageMixin

from django.db import models


class TopicPage(Page):
    parent_page_types = ['domestic.DomesticHomePage']
    subpages_types = ['learn.PersonalisedLessonPage']

    description = models.TextField()

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]


class LessonPage(PersonalisablePageMixin, Page):
    parent_page_types = ['learn.TopicPage']

    generic_content = StreamField([
        ('generic_content', PersonalisedStructBlock([('paragraph', blocks.RichTextBlock())], icon='pilcrow'))
    ])
    country_specific_content = StreamField([
        ('country_specific_content', PersonalisedStructBlock([('paragraph', blocks.RichTextBlock())], icon='pilcrow'))
    ])
    product_specific_content = StreamField([
        ('product_specific_content', PersonalisedStructBlock([('paragraph', blocks.RichTextBlock())], icon='pilcrow'))
    ])

    order = models.PositiveSmallIntegerField(null=True, blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('generic_content'),
        StreamFieldPanel('country_specific_content'),
        StreamFieldPanel('product_specific_content')
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('order')
    ]

    class Meta:
        ordering = ['order']

    def get_last_object(self):
        return self.get_siblings().exclude(pk=self.pk).order_by('-order')[0]

    def check_collision(self, proposed_order):
        return self.get_siblings().filter(order=proposed_order).exists()

    def save(self, *args, **kwargs):
        if self.order is None:
            try:
                last_object = self.get_last_object()
                self.order = last_object.order + 1
            except ObjectDoesNotExist:
                self.order = 1  # first sibling under the parent

        return super().save(*args, **kwargs)
