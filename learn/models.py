from directory_constants import choices
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail_personalisation.blocks import PersonalisedStructBlock
from wagtail_personalisation.models import PersonalisablePageMixin

from django.shortcuts import redirect
from django.db import models

from core.models import TimeStampedModel
from core import mixins


class TopicPage(Page):
    parent_page_types = ['domestic.DomesticHomePage']
    subpage_types = ['learn.LessonPage']

    description = models.TextField()

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        queryset = LessonViewHit.objects.filter(topic=self, sso_id=request.user.pk)
        context['is_read_collection'] = queryset.values_list('lesson__pk', flat=True)
        return context


class LessonPage(PersonalisablePageMixin, Page):
    parent_page_types = ['learn.TopicPage']

    generic_content = StreamField([
        (
            'generic_content', PersonalisedStructBlock(
                [('paragraph', blocks.RichTextBlock())],
                template='core/personalised_page_struct_block.html',
                icon='pilcrow'
            )
        )
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

    def serve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            LessonViewHit.objects.get_or_create(
                lesson=self,
                topic=self.get_parent().specific,
                sso_id=request.user.pk,
            )
        return super().serve(request, **kwargs)

    def get_context(self, request):
        context = super().get_context(request)
        context['is_read'] = self.read_hits.filter(sso_id=request.user.pk).exists()
        context['topics'] = TopicPage.objects.live()
        context['country_choices'] = [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES]
        return context


class LessonViewHit(TimeStampedModel):
    lesson = models.ForeignKey(LessonPage, on_delete=models.CASCADE, related_name='read_hits')
    topic = models.ForeignKey(TopicPage, on_delete=models.CASCADE, related_name='read_hits_topic')
    sso_id = models.TextField()

    class Meta:
        ordering = ['lesson__pk']
        unique_together = ['lesson', 'topic', 'sso_id']


class LearnPage(mixins.WagtailAdminExclusivePageMixin, mixins.EnableTourMixin, Page):
    parent_page_types = ['domestic.DomesticHomePage']
