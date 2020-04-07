import hashlib

from core.context import get_context_provider
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel, \
    ObjectList, TabbedInterface
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.utils.decorators import cached_classmethod
from wagtail_personalisation.blocks import PersonalisedStructBlock
from wagtail_personalisation.models import PersonalisablePageMixin
from wagtail.snippets.models import register_snippet

from django.db import models


class AbstractObjectHash(models.Model):
    class Meta:
        abstract = True

    content_hash = models.CharField(max_length=1000)

    @staticmethod
    def generate_content_hash(field_file):
        filehash = hashlib.md5()
        field_file.open()
        filehash.update(field_file.read())
        field_file.close()
        return filehash.hexdigest()


class DocumentHash(AbstractObjectHash):
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )


class ImageHash(AbstractObjectHash):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )


class AltTextImage(AbstractImage):
    alt_text = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ('alt_text',)


class Rendition(AbstractRendition):
    image = models.ForeignKey(AltTextImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'))


@register_snippet
class Tour(ClusterableModel):
    page = models.OneToOneField('wagtailcore.Page', on_delete=models.CASCADE, related_name='tour')
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    button_text = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('page'),
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('button_text'),
        MultiFieldPanel([InlinePanel('steps')], heading='Steps'),
    ]

    def __str__(self):
        return self.page.title


class TourStep(Orderable):
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    selector = models.CharField(max_length=255)
    tour = ParentalKey(Tour, on_delete=models.CASCADE, related_name='steps')

    panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('position'),
        FieldPanel('selector'),
    ]


@register_snippet
class Product(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name


@register_snippet
class Country(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'


class TimeStampedModel(models.Model):
    """Modified version of django_extensions.db.models.TimeStampedModel

    Unfortunately, because null=True needed to be added to create and
    modified fields, inheritance causes issues with field clash.

    """
    created = CreationDateTimeField('created', null=True)
    modified = ModificationDateTimeField('modified', null=True)

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super().save(**kwargs)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True


# Content models

class CMSGenericPage(PersonalisablePageMixin, Page):
    """
    Generic page, freely inspired by Codered page
    """

    class Meta:
        abstract = True

    # Do not allow this page type to be created in wagtail admin
    is_creatable = False

    template_choices = []

    ################
    # Content fields
    ################

    body = StreamField([
        (
            'body', PersonalisedStructBlock(
                [('paragraph', blocks.RichTextBlock())],
                template='core/personalised_page_struct_block.html',
                icon='pilcrow'
            )
        )
    ])

    ###############
    # Settings fields
    ###############

    track_user_page_view = models.BooleanField(
        default=False,
        help_text='Should we record when a user views a page?',
    )

    ###############
    # Layout fields
    ###############

    template = models.CharField(
        max_length=255,
        choices=None,
    )

    #########
    # Panels
    #########

    settings_panels = Page.settings_panels + ['track_user_page_view']
    content_panels = Page.content_panels + [StreamFieldPanel('body')]
    layout_panels = [FieldPanel('template')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self._meta.get_field('template')
        field.choices = self.template_choices
        field.required = True

    @cached_classmethod
    def get_edit_handler(cls):  # NOQA N805
        panels = [
            ObjectList(cls.content_panels, heading='Content'),
            ObjectList(cls.layout_panels, heading='Layout'),
            ObjectList(cls.settings_panels, heading='Settings', classname='settings'),
        ]

        return TabbedInterface(panels).bind_to(model=cls)

    def get_template(self, request, *args, **kwargs):
        return self.template

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        if self.track_user_page_view and request.user.is_authenticated:
            queryset = PageView.objects.filter(page=self, sso_id=request.user.pk)
            context['is_read_collection'] = queryset.values_list('page__pk', flat=True)

        provider = get_context_provider(request=request, page=self)
        if provider:
            context.update(provider.get_context_data(request=request, page=self))
        return context

    def serve(self, request, *args, **kwargs):
        if self.track_user_page_view and request.user.is_authenticated:
            PageView.objects.get_or_create(
                page=self,
                list_page=self.get_parent().specific,
                sso_id=request.user.pk,
            )
        return super().serve(request, **kwargs)


class ListPage(CMSGenericPage):
    parent_page_types = ['domestic.DomesticHomePage']
    subpage_types = ['core.DetailPage']

    template_choices = (
        ('export_plan/listing.html', 'Export plan'),
        ('learn/listing.html', 'Learn')
    )


class DetailPage(CMSGenericPage):
    parent_page_types = ['core.ListPage']
    template_choices = (
        ('export_plan/detail.html', 'Export plan'),
        ('learn/lesson_page.html', 'Lesson')
    )


class PageView(TimeStampedModel):
    page = models.ForeignKey(DetailPage, on_delete=models.CASCADE, related_name='page_views')
    list_page = models.ForeignKey(ListPage, on_delete=models.CASCADE, related_name='page_views_list')
    sso_id = models.TextField()

    class Meta:
        ordering = ['lesson__pk']
        unique_together = ['page', 'sso_id', 'sso_id']
