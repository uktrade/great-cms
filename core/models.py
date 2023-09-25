import hashlib
import mimetypes
from urllib.parse import unquote

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import Select
from django.http import Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from great_components.mixins import GA360Mixin
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ClusterableModel, ParentalKey
from taggit.managers import TaggableManager
from taggit.models import ItemBase, TagBase, TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock, StreamBlockValidationError
from wagtail.contrib.redirects.models import Redirect
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtail.utils.decorators import cached_classmethod
from wagtailmedia.models import Media
from wagtailseo.models import SeoMixin

from core import blocks as core_blocks, cms_panels, mixins, snippet_slugs
from core.blocks import (
    LinkBlockWithHeading,
    MicrositeColumnBlock,
    SupportCardBlock,
    SupportTopicCardBlock,
)
from core.case_study_index import delete_cs_index, update_cs_index
from core.cms_snippets import NonPageContentSEOMixin, NonPageContentSnippetBase
from core.constants import (
    BACKLINK_QUERYSTRING_NAME,
    RICHTEXT_FEATURES__MINIMAL,
    RICHTEXT_FEATURES__REDUCED,
)
from core.context import get_context_provider
from core.utils import PageTopicHelper, get_first_lesson
from exportplan.core.data import (
    SECTION_SLUGS as EXPORTPLAN_SLUGS,
    SECTIONS as EXPORTPLAN_URL_MAP,
)

# If we make a Redirect appear as a Snippet, we can sync it via Wagtail-Transfer
register_snippet(Redirect)


class GreatMedia(Media):
    description = models.TextField(
        verbose_name=_('Description'), blank=True, null=True  # left null because was an existing field
    )

    transcript = models.TextField(
        verbose_name=_('Transcript'), blank=False, null=True  # left null because was an existing field
    )

    subtitles_en = models.TextField(
        verbose_name=_('English subtitles'),
        null=True,
        blank=True,
        help_text='English-language subtitles for this video, in VTT format',
    )

    admin_form_fields = Media.admin_form_fields + ('transcript', 'subtitles_en', 'description')

    def save(self, *args, **kwargs):
        self.file._committed = True
        self.file.name = f'media/{self.file.name}'
        return super().save(*args, **kwargs)

    @property
    def sources(self):
        return [
            {
                'src': self.url,
                'type': mimetypes.guess_type(self.filename)[0] or 'application/octet-stream',
                'transcript': self.transcript,
            }
        ]

    @property
    def subtitles(self):
        output = []
        # TO COME: support for more than just English
        if self.subtitles_en:
            output.append(
                {
                    'srclang': 'en',
                    'label': 'English',
                    'url': reverse('core:subtitles-serve', args=[self.id, 'en']),
                    'default': False,
                },
            )
        return output


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
        'wagtaildocs.Document', null=True, blank=True, on_delete=models.CASCADE, related_name='+'
    )


class ImageHash(AbstractObjectHash):
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.CASCADE, related_name='+')


class AltTextImage(AbstractImage):
    alt_text = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ('alt_text',)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images List'


class Rendition(AbstractRendition):
    image = models.ForeignKey(AltTextImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = ('image', 'filter_spec', 'focal_point_key')

    @property
    def alt(self):
        return self.image.alt_text if self.image.alt_text else self.image.default_alt_text


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
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    panels = [FieldPanel('name')]

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


@register_snippet
class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    iso2 = models.CharField(max_length=2, null=True, blank=True)
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL)

    panels = [
        FieldPanel('name'),
        FieldPanel('iso2'),
        FieldPanel('region'),
    ]

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def save(self, *args, **kwargs):
        # Automatically set slug on save, if not already set
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


@register_snippet
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    panels = [FieldPanel('name')]

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


@register_snippet
class IndustryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ForeignKey(
        AltTextImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [FieldPanel('name'), FieldPanel('icon')]

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class SpeakerOrderable(Orderable):
    """
    This allows us to select one or more speakers.
    """

    page = ParentalKey('export_academy.Event', related_name='event_speakers')
    speaker = models.ForeignKey('core.Speaker', on_delete=models.CASCADE)

    panels = [FieldPanel('speaker')]


@register_snippet
class Speaker(ClusterableModel):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    organisation = models.CharField(max_length=255)
    description = RichTextField(features=[])

    panels = [
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('organisation'),
        FieldPanel('description'),
    ]

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.role)


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
        ordering = (
            '-modified',
            '-created',
        )
        abstract = True


# Content models


class CMSGenericPage(
    SeoMixin,
    mixins.EnableTourMixin,
    mixins.AuthenticatedUserRequired,
    mixins.WagtailGA360Mixin,
    GA360Mixin,
    Page,
):
    """
    Generic page, freely inspired by Codered page
    """

    class Meta:
        abstract = True

    # Do not allow this page type to be created in wagtail admin
    is_creatable = False
    template_choices = []

    ###############
    # Layout fields
    ###############
    template = models.CharField(
        max_length=255,
        choices=None,
    )

    #########
    # Panels
    ##########
    layout_panels = [FieldPanel('template')]
    settings_panels = [FieldPanel('slug')] + Page.settings_panels

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

        return TabbedInterface(panels).bind_to_model(model=cls)

    def get_template(self, request, *args, **kwargs):
        return self.template

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        self.set_ga360_payload(
            page_id=self.id,
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section=str(self.url or '/').split('/')[1],
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        provider = get_context_provider(request=request, page=self)
        if provider:
            context.update(provider.get_context_data(request=request, page=self))
        return context


class LandingPage(CMSGenericPage):
    parent_page_types = [
        'domestic.DomesticHomePage',  # TODO: once we've restructured, remove this permission
        'domestic.GreatDomesticHomePage',
    ]
    subpage_types = [
        'core.ListPage',
        'core.InterstitialPage',
        'domestic.DomesticDashboard',
    ]
    template_choices = (
        ('learn/landing_page.html', 'Learn'),
        ('core/generic_page.html', 'Generic'),
    )

    ################
    # Content fields
    ################
    description = RichTextField()
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], use_json_field=True, null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    body = StreamField(
        [
            ('section', core_blocks.SectionBlock()),
            ('title', core_blocks.TitleBlock()),
            ('text', blocks.RichTextBlock(icon='openquote', helptext='Add a textblock')),
            ('image', core_blocks.ImageBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    components = StreamField(
        [
            ('route', core_blocks.RouteSectionBlock()),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('description'),
        FieldPanel('button'),
        FieldPanel('image'),
        FieldPanel('components'),
        FieldPanel('body'),
    ]


class InterstitialPage(CMSGenericPage):
    parent_page_types = ['core.LandingPage']
    template_choices = (('learn/interstitial.html', 'Learn'),)

    ################
    # Content fields
    ################
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], use_json_field=True, null=True, blank=True)

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('button'),
    ]


class ListPage(CMSGenericPage):
    parent_page_types = ['core.LandingPage']
    subpage_types = ['core.CuratedListPage']

    template_choices = (('learn/automated_list_page.html', 'Learn'),)

    record_read_progress = models.BooleanField(
        default=False,
        help_text='Should we record when a user views a page in this collection?',
    )

    class Meta:
        verbose_name = 'Automated list page'
        verbose_name_plural = 'Automated list pages'

    def get_context(self, request, *args, **kwargs):
        from core.helpers import get_high_level_completion_progress
        from domestic.helpers import (
            get_last_completed_lesson_id,
            get_lesson_completion_status,
        )

        context = super().get_context(request)

        if request.user.is_authenticated:
            lesson_id = get_last_completed_lesson_id(request.user)
            if lesson_id:
                page = DetailPage.objects.get(id=lesson_id)
                page_topic_helper = PageTopicHelper(page)
                next_lesson = page_topic_helper.get_next_lesson()
                if next_lesson:
                    context['next_lesson'] = next_lesson
                else:
                    next_module = page.module.get_next_sibling()
                    if next_module:
                        context['next_lesson'] = get_first_lesson(next_module)

            completion_status = get_lesson_completion_status(request.user)
            context['high_level_completion_progress'] = get_high_level_completion_progress(
                completion_status=completion_status,
            )

        return context

    ################
    # Content fields
    ################
    description = RichTextField()
    button_label = models.CharField(max_length=100)

    #########
    # Panels
    #########
    settings_panels = CMSGenericPage.settings_panels + [FieldPanel('record_read_progress')]
    content_panels = CMSGenericPage.content_panels + [FieldPanel('description'), FieldPanel('button_label')]


class CuratedListPage(CMSGenericPage):
    parent_page_types = ['core.ListPage']
    subpage_types = [
        'core.TopicPage',
    ]
    template_choices = (('learn/curated_list_page.html', 'Learn'),)

    ################
    # Content fields
    ################
    heading = RichTextField()
    image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    ########
    # Panels
    ########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('heading'),
        FieldPanel('image'),
    ]

    def get_topics(self, live=True) -> models.QuerySet:
        qs = TopicPage.objects.live().specific().descendant_of(self)
        if live:
            qs = qs.live()
        return qs

    @cached_property
    def count_topics(self):
        return self.get_topics().count()

    @cached_property
    def count_detail_pages(self):
        count = 0
        for topic in self.get_topics():
            count += DetailPage.objects.live().descendant_of(topic).count()
        return count

    def get_context(self, request, *args, **kwargs):
        from core.helpers import (
            get_high_level_completion_progress,
            get_module_completion_progress,
        )
        from domestic.helpers import get_lesson_completion_status

        context = super().get_context(request)
        # Give the template a simple way to link back to the parent
        # learning module (ListPage)
        context['parent_page_url'] = self.get_parent().url

        if request.user.is_authenticated:
            # get this once, so we don't waste the network call to get the data twice
            completion_status = get_lesson_completion_status(request.user)
            context['module_completion_progress'] = get_module_completion_progress(
                completion_status=completion_status,
                module_page=self,
            )
            context['high_level_completion_progress'] = get_high_level_completion_progress(
                completion_status=completion_status,
            )
        return context


def hero_singular_validation(value):
    if value and len(value) > 1:
        raise StreamBlockValidationError(
            non_block_errors=ValidationError('Only one image or video allowed in Hero section', code='invalid'),
        )


class TopicPage(mixins.AuthenticatedUserRequired, Page):
    """Structural page to allow for cleaner mapping of lessons (`DetailPage`s)
    to modules (`CuratedListPage`s).

    Not intented to be viewed by end users, so will redirect to the parent
    module if accessed.

    Also, for the above reason, mixins.WagtailGA360Mixin and GA360Mixin
    are not used."""

    parent_page_types = ['core.CuratedListPage']
    subpage_types = [
        'core.DetailPage',
        'core.LessonPlaceholderPage',
    ]

    # `title` comes from Page superclass and that's all we need here

    def _redirect_to_parent_module(self):
        return HttpResponseRedirect(self.get_parent().url)

    def serve_preview(self, request, mode_name='dummy'):
        # It doesn't matter what is passed as mode_name - we always redirect
        return self._redirect_to_parent_module()

    def serve(self, request):
        return self._redirect_to_parent_module()


class LessonPlaceholderPage(mixins.AuthenticatedUserRequired, Page):

    """Structural page to allow for configuring and representing very simple
    to modules (`CuratedListPage`s).

    Not intented to be viewed by end users, so will redirect to the parent
    module if accessed.

    Also, for the above reason, mixins.WagtailGA360Mixin and GA360Mixin
    are not used."""

    parent_page_types = ['core.TopicPage']
    subpage_types = []  # No child pages allowed for placeholders

    # `title` comes from Page superclass and that's all we need here

    def _redirect_to_parent_module(self):
        dest = CuratedListPage.objects.ancestor_of(self).first().url
        return HttpResponseRedirect(dest)

    def serve_preview(self, request, mode_name='dummy'):
        # It doesn't matter what is passed as mode_name - we always redirect
        return self._redirect_to_parent_module()

    def serve(self, request):
        return self._redirect_to_parent_module()


class DetailPage(CMSGenericPage):
    estimated_read_duration = models.DurationField(null=True, blank=True)
    parent_page_types = [
        'core.CuratedListPage',  # TEMPORARY: remove after topics refactor migration has run
        'core.TopicPage',
    ]
    template_choices = (('learn/detail_page.html', 'Learn'),)

    class Meta:
        verbose_name = 'Detail page'
        verbose_name_plural = 'Detail pages'

    ################
    # Content fields
    ################
    hero = StreamField(
        [
            ('Image', core_blocks.ImageBlock(template='core/includes/_hero_image.html')),
            ('Video', core_blocks.SimpleVideoBlock(template='core/includes/_hero_video.html')),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        validators=[hero_singular_validation],
    )
    objective = StreamField(
        [
            (
                'paragraph',
                blocks.RichTextBlock(options={'class': 'objectives'}),
            ),
            ('ListItem', core_blocks.Item()),
        ],
        use_json_field=True,
    )
    body = StreamField(
        [
            (
                'paragraph',
                blocks.StructBlock(
                    [('paragraph', blocks.RichTextBlock())],
                    template='core/struct_paragraph_block.html',
                    icon='font',
                ),
            ),
            (
                'video',
                blocks.StructBlock(
                    [('video', core_blocks.VideoBlock())],
                    template='core/struct_video_block.html',
                    icon='play',
                ),
            ),
            ('case_study', core_blocks.CaseStudyStaticBlock(icon='fa-book')),
            (
                'Step',
                core_blocks.StepByStepBlock(icon='cog'),
            ),
            (
                'fictional_example',
                blocks.StructBlock(
                    [('fiction_body', blocks.RichTextBlock(icon='openquote'))],
                    template='learn/fictional_company_example.html',
                    icon='comment-dots',
                ),
            ),
            (
                'ITA_Quote',
                core_blocks.ITAQuoteBlock(icon='quote-left'),
            ),
            (
                'pros_cons',
                blocks.StructBlock(
                    [
                        (
                            'pros',
                            blocks.StreamBlock(
                                [
                                    (
                                        'item',
                                        core_blocks.Item(icon='arrow-right'),
                                    )
                                ]
                            ),
                        ),
                        (
                            'cons',
                            blocks.StreamBlock(
                                [
                                    (
                                        'item',
                                        core_blocks.Item(icon='arrow-right'),
                                    )
                                ]
                            ),
                        ),
                    ],
                    template='learn/pros_and_cons.html',
                    icon='arrow-right',
                ),
            ),
            ('choose_do_not_choose', core_blocks.ChooseDoNotChooseBlock()),
            (
                'image',
                core_blocks.ImageBlock(
                    template='core/includes/_image_full_width.html',
                    help_text='Image displayed within a full-page-width block',
                ),
            ),
            (
                'video',
                core_blocks.SimpleVideoBlock(
                    template='core/includes/_video_full_width.html',
                    help_text='Video displayed within a full-page-width block',
                ),
            ),
        ],
        use_json_field=True,
    )
    recap = StreamField(
        [
            (
                'recap_item',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock(icon='heading')),
                        (
                            'item',
                            blocks.StreamBlock(
                                [
                                    (
                                        'item',
                                        core_blocks.Item(),
                                    )
                                ]
                            ),
                        ),
                    ],
                    template='learn/recap.html',
                    icon='comment-dots',
                ),
            )
        ],
        use_json_field=True,
    )

    #########
    # Panels
    ##########
    content_panels = Page.content_panels + [
        FieldPanel('hero'),
        FieldPanel('objective'),
        FieldPanel('body'),
        FieldPanel('recap'),
    ]

    def handle_page_view(self, request):
        if request.user.is_authenticated:
            # checking if the page should record read progress
            # checking if the page is already marked as read
            list_page = (
                ListPage.objects.ancestor_of(self)
                .filter(record_read_progress=True)
                .exclude(page_views_list__sso_id=request.user.pk, page_views_list__page=self)
                .first()
            )
            if list_page:
                PageView.objects.get_or_create(
                    page=self,
                    list_page=list_page,
                    sso_id=request.user.pk,
                )

    def serve(self, request, *args, **kwargs):
        self.handle_page_view(request)
        return super().serve(request, **kwargs)

    @cached_property
    def topic_title(self):
        return self.get_parent().title

    @cached_property
    def module(self):
        """Gets the learning module this lesson belongs to"""
        return CuratedListPage.objects.live().specific().ancestor_of(self).first()

    @cached_property
    def _export_plan_url_map(self):
        """Return a lookup dictionary of URL Slugs->title for all the
        Export Plan sections we have."""
        return {url: values['title'] for url, values in EXPORTPLAN_URL_MAP.items()}

    def _get_backlink(self, request):
        """Try to extract a backlink (used for a link to the export plan) from the
        querystring on the request that brought us to this view.

        Only accepts backlinks that we KNOW are for the export plan, else ignore it."""

        backlink_path = request.GET.get(BACKLINK_QUERYSTRING_NAME, '')
        if backlink_path is not None:
            backlink_path = unquote(backlink_path)
            if len(backlink_path.split('/')) > 2 and (
                backlink_path.split('/')[3] in EXPORTPLAN_SLUGS and '://' not in backlink_path
            ):
                # The check for '://' will stop us accepting a backlink which
                # features a full URL as its OWN querystring param (eg a crafted attack
                # URL), but that's an acceptable limitation here and is very unlikely
                # to happen.
                return backlink_path

        return None  # safe default

    def _get_backlink_title(self, backlink_path):
        """For a given backlink, see if we can get a title that goes with it.
        For now, this is limited only to Export Plan pages/links.
        """
        # We have to re-arrange EXPORT_PLAN_SECTION_TITLES_URLS after import
        # because it features lazily-evaluated URLs that aren't ready when
        # models are imported

        if backlink_path and len(backlink_path.split('/')) > 3:
            _path = backlink_path.split('/')[3]
            return self._export_plan_url_map.get(_path)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        context['refresh_on_market_change'] = True
        # Prepare backlink to the export plan if we detect one and can validate it
        _backlink = self._get_backlink(request)
        if _backlink:
            context['backlink'] = _backlink
            context['backlink_title'] = self._get_backlink_title(_backlink)

        if isinstance(self.get_parent().specific, TopicPage):
            # In a conditional because a DetailPage currently MAY be used as
            # a child of another page type...
            page_topic_helper = PageTopicHelper(self)
            next_lesson = page_topic_helper.get_next_lesson()
            context['current_lesson'] = self
            context['current_module'] = page_topic_helper.module
            if page_topic_helper:
                topic_page = page_topic_helper.get_page_topic()
                if topic_page:
                    context['current_topic'] = topic_page
                    context['page_topic'] = topic_page.title

            if next_lesson:
                context['next_lesson'] = next_lesson
            else:
                next_module = self.module.get_next_sibling()
                if not next_module:
                    return context
                context['next_module'] = next_module.specific
                context['next_lesson'] = get_first_lesson(next_module)
        return context


class PageView(TimeStampedModel):
    page = models.ForeignKey(DetailPage, on_delete=models.CASCADE, related_name='page_views')
    list_page = models.ForeignKey(ListPage, on_delete=models.CASCADE, related_name='page_views_list')
    sso_id = models.TextField()

    class Meta:
        ordering = ['page__pk']
        unique_together = ['page', 'sso_id']


# TODO: deprecate and remove
class ContentModuleTag(TaggedItemBase):
    content_object = ParentalKey('core.ContentModule', on_delete=models.CASCADE, related_name='tagged_items')


# TODO: deprecate and remove
@register_snippet
class ContentModule(ClusterableModel):
    title = models.CharField(max_length=255)
    content = RichTextField()
    tags = TaggableManager(through=ContentModuleTag, blank=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('content'),
        FieldPanel('tags'),
    ]

    def __str__(self):
        return self.title


class PersonalisationHSCodeTag(TagBase):
    """Custom tag for personalisation.
    Tag value will be a HS6, HS4 or HS2 code"""

    # free_tagging = False  # DISABLED until tag data only comes via data migration

    class Meta:
        verbose_name = 'HS Code tag for personalisation'
        verbose_name_plural = 'HS Code tags for personalisation'


class PersonalisationCountryTag(TagBase):
    """Custom tag for personalisation.
    Tag value will be an ISO-2 Country code ('DE')
    """

    free_tagging = False

    class Meta:
        verbose_name = 'Country tag for personalisation'
        verbose_name_plural = 'Country tags for personalisation'


class PersonalisationRegionTag(TagBase):
    """Custom tag for personalisation.
    Tag value will be a geographical string ('Europe')
    """

    free_tagging = False

    class Meta:
        verbose_name = 'Region tag for personalisation'
        verbose_name_plural = 'Region tags for personalisation'


class PersonalisationTradingBlocTag(TagBase):
    """Custom tag for personalisation.
    Tag value will be an Trading blocs
    """

    free_tagging = False

    class Meta:
        verbose_name = 'Trading bloc tag for personalisation'
        verbose_name_plural = 'Trading bloc tags for personalisation'


# If you're wondering what's going on here:
# https://docs.wagtail.io/en/stable/reference/pages/model_recipes.html#custom-tag-models


class HSCodeTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationHSCodeTag, related_name='hscode_tagged_case_studies', on_delete=models.CASCADE
    )
    content_object = ParentalKey(to='core.CaseStudy', on_delete=models.CASCADE, related_name='hs_code_tagged_items')


class CountryTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationCountryTag, related_name='country_tagged_case_studies', on_delete=models.CASCADE
    )
    content_object = ParentalKey(to='core.CaseStudy', on_delete=models.CASCADE, related_name='country_tagged_items')


class RegionTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationRegionTag, related_name='region_tagged_case_studies', on_delete=models.CASCADE
    )
    content_object = ParentalKey(to='core.CaseStudy', on_delete=models.CASCADE, related_name='region_tagged_items')


class TradingBlocTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationTradingBlocTag, related_name='trading_bloc_tagged_case_studies', on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to='core.CaseStudy', on_delete=models.CASCADE, related_name='trading_bloc_tagged_items'
    )


def _high_level_validation(value, error_messages):
    TEXT_BLOCK = 'text'  # noqa N806
    MEDIA_BLOCK = 'media'  # noqa N806
    QUOTE_BLOCK = 'quote'  # noqa N806

    # we need to be strict about presence and ordering of these nodes
    if [node.block_type for node in value if node.block_type != QUOTE_BLOCK] != [MEDIA_BLOCK, TEXT_BLOCK]:
        error_messages.append(
            (
                'This block must contain one Media section (with one or '
                'two items in it) and/or a Quote section, then one Text section following it.'
            )
        )

    return error_messages


def _low_level_validation(value, error_messages):
    # Check content of media node, which should be present here

    MEDIA_BLOCK = 'media'  # noqa N806
    VIDEO_BLOCK = 'video'  # noqa N806

    for node in value:
        if node.block_type == MEDIA_BLOCK:
            subnode_block_types = [subnode.block_type for subnode in node.value]
            if len(subnode_block_types) == 2:
                if set(subnode_block_types) == {VIDEO_BLOCK}:
                    # Two videos: not allowed
                    error_messages.append('Only one video may be used in a case study.')
                elif subnode_block_types[1] == VIDEO_BLOCK:
                    # implicitly, [0] must be an image
                    # video after image: not allowed
                    error_messages.append('The video must come before a still image.')

    return error_messages


def case_study_body_validation(value):
    """Ensure the case study has exactly both a media node and a text node
    and that the media node has the following content:
        * One image, only
        * One video, only
        * One video + One image
            * (video must comes first so that it is displayed first)
        * Two images
    """

    error_messages = []

    if value:
        error_messages = _high_level_validation(value, error_messages)
        error_messages = _low_level_validation(value, error_messages)

        if error_messages:
            raise StreamBlockValidationError(
                non_block_errors=ValidationError('; '.join(error_messages), code='invalid'),
            )


class MagnaPageChooserPanel(PageChooserPanel):
    show_label = False

    field_template = 'admin/wagtailadmin/edit_handlers/field_panel_field.html'

    def render_html(self):
        instance_obj = self.get_chosen_item()
        context = {
            'field': self.bound_field,
            self.object_type_name: instance_obj,
            'is_chosen': bool(instance_obj),  # DEPRECATED - passed to templates for backwards compatibility only
            # Added obj_type on base class method render_html
            'obj_type': instance_obj.specific.__class__.__name__ if instance_obj else None,
        }
        return mark_safe(render_to_string(self.field_template, context))


class CaseStudyRelatedPages(Orderable):
    case_study = ParentalKey(
        'core.CaseStudy',
        related_name='related_pages',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    page = models.ForeignKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='+',
    )
    panels = [
        MagnaPageChooserPanel('page', [DetailPage, CuratedListPage, TopicPage]),
    ]

    class Meta:
        unique_together = ['case_study', 'page']


@register_snippet
class CaseStudy(ClusterableModel):
    """Dedicated snippet for use as a case study. Supports personalised
    selection via its tags.

    The decision about the appropriate Case Study block to show will happen
    when the page attempts to render the relevant CaseStudyBlock.

    Note that this is rendered via Wagtail's ModelAdmin, so appears in the sidebar,
    but we have to keep it registered as a Snippet to be able to transfer it
    with Wagtail-Transfer
    """

    title = models.CharField(
        max_length=255,
        blank=False,
        verbose_name='Internal case study title',
    )

    # old name company_name
    summary_context = models.CharField(max_length=255, blank=False, default='How we did it')
    # old name summary
    lead_title = models.TextField(blank=False)  # Deliberately not rich-text / no formatting
    body = StreamField(
        [
            (
                'media',
                blocks.StreamBlock(
                    [
                        ('video', core_blocks.SimpleVideoBlock(template='core/includes/_case_study_video.html')),
                        ('image', core_blocks.ImageBlock()),
                    ],
                    min_num=1,
                    max_num=2,
                ),
            ),
            (
                'text',
                blocks.RichTextBlock(
                    features=RICHTEXT_FEATURES__MINIMAL,
                ),
            ),
            (
                'quote',
                core_blocks.CaseStudyQuoteBlock(),
            ),
        ],
        use_json_field=True,
        validators=[case_study_body_validation],
        help_text=(
            'This block must contain one Media section (with one or two items in it) '
            'and/or Quote sections, then one Text section.'
        ),
    )

    # We are keeping the personalisation-relevant tags in separate
    # fields to aid lookup and make the UX easier for editors
    hs_code_tags = ClusterTaggableManager(through='core.HSCodeTaggedCaseStudy', blank=True, verbose_name='HS-code tags')

    country_code_tags = ClusterTaggableManager(
        through='core.CountryTaggedCaseStudy', blank=True, verbose_name='Country tags'
    )
    region_code_tags = ClusterTaggableManager(
        through='core.RegionTaggedCaseStudy', blank=True, verbose_name='Region tags'
    )
    trading_bloc_code_tags = ClusterTaggableManager(
        through='core.TradingBlocTaggedCaseStudy', blank=True, verbose_name='Trading bloc tags'
    )

    created = CreationDateTimeField('created', null=True)
    modified = ModificationDateTimeField('modified', null=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('lead_title'),
                FieldPanel('summary_context'),
                FieldPanel('body'),
            ],
            heading='Case Study content',
        ),
        MultiFieldPanel(
            [
                FieldPanel('hs_code_tags'),
                FieldPanel('country_code_tags'),
                FieldPanel('region_code_tags'),
                FieldPanel('trading_bloc_code_tags'),
            ],
            heading='Case Study tags for Personalisation',
        ),
        MultiFieldPanel(
            [
                InlinePanel('related_pages', label='Related pages'),
            ],
            heading='Related Lesson, Topic & Module, also used for Personalisation',
        ),
    ]

    def __str__(self):
        display_name = self.title if self.title else self.summary_context
        return f'{display_name}'

    def save(self, **kwargs):
        # When we create a new CS need to call create to obtain an ID for indexing
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super().save(**kwargs)
        update_cs_index(self)

    def delete(self, **kwargs):
        delete_cs_index(self.id)
        super().delete(**kwargs)

    def get_cms_standalone_view_url(self):
        return reverse('cms_extras:case-study-view', args=[self.id])

    class Meta:
        verbose_name_plural = 'Case studies'
        get_latest_by = 'modified'
        ordering = (
            '-modified',
            '-created',
        )


@register_setting
class CaseStudyScoringSettings(BaseSiteSetting):
    threshold = models.DecimalField(
        help_text='This is the minimum score which a case study needs to have to be '
        'considered before being presented to users. ',
        default=10,
        decimal_places=3,
        max_digits=5,
    )
    lesson = models.DecimalField(
        help_text="Score given when user's lesson is tagged in the case study.",
        default=8,
        decimal_places=3,
        max_digits=5,
    )
    topic = models.DecimalField(
        help_text="Score given when user's lesson's topic is tagged in the case study "
        'unless there is also lesson match.',
        default=4,
        decimal_places=3,
        max_digits=5,
    )
    module = models.DecimalField(
        help_text="Score given when the user's lesson's module is tagged in the case study "
        'unless there is also lesson or topic match.',
        default=2,
        decimal_places=3,
        max_digits=5,
    )
    product_hs6 = models.DecimalField(
        help_text='Score given when any case study HS6 tag matches the complete HS6 code of '
        "any of the user's products",
        default=8,
        decimal_places=3,
        max_digits=5,
    )
    product_hs4 = models.DecimalField(
        help_text="Score given when any case study HS4 tag matches the first 4 digits of any of the user's products "
        'unless there is an HS6 match.',
        default=4,
        decimal_places=3,
        max_digits=5,
    )
    product_hs2 = models.DecimalField(
        help_text="Score given when any case study HS2 tag matches the first 2 digits of any of the user's products "
        'unless there is an HS6 or HS4 match.',
        default=2,
        decimal_places=3,
        max_digits=5,
    )
    country_exact = models.DecimalField(
        help_text="Score given when any case study country tag exactly matches one of the user's export markets.",
        default=4,
        decimal_places=3,
        max_digits=5,
    )
    country_region = models.DecimalField(
        help_text="Score given when any case study region tag matches the region of any of the user's export markets "
        'unless there is an exact country match.',
        default=2,
        decimal_places=3,
        max_digits=5,
    )

    trading_blocs = models.DecimalField(
        help_text='Score given when any case study trading bloc tag matches the any trading bloc that any of '
        "the user's export markets falls into unless there is an exact country or region match.",
        default=2,
        decimal_places=3,
        max_digits=5,
    )

    product_tab = [MultiFieldPanel([FieldPanel('product_hs6'), FieldPanel('product_hs4'), FieldPanel('product_hs2')])]
    market_tab = [
        MultiFieldPanel([FieldPanel('country_exact'), FieldPanel('country_region'), FieldPanel('trading_blocs')])
    ]
    lesson_tab = [MultiFieldPanel([FieldPanel('lesson'), FieldPanel('topic'), FieldPanel('module')])]

    threshold_tab = [
        MultiFieldPanel(
            [
                FieldPanel('threshold'),
            ]
        )
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(product_tab, heading='Product'),
            ObjectList(market_tab, heading='Market'),
            ObjectList(lesson_tab, heading='Lesson'),
            ObjectList(threshold_tab, heading='Threshold'),
        ]
    )

    class Meta:
        verbose_name = 'Case Study Scoring'


class Microsite(Page):
    folder_page = True
    settings_panels = [FieldPanel('slug')]

    parent_page_types = [
        'domestic.DomesticHomePage',
        'domestic.GreatDomesticHomePage',
    ]

    subpage_types = ['core.MicrositePage']

    class Meta:
        verbose_name = 'Campaign site'
        verbose_name_plural = 'Campaign sites'

    def serve_preview(self, request, mode_name='dummy'):
        # It doesn't matter what is passed as mode_name - we always HTTP404
        raise Http404()

    def serve(self, request):
        raise Http404()


class MicrositePage(cms_panels.MicrositePanels, Page):
    template = 'microsites/micro_site_page.html'
    parent_page_types = [
        'core.Microsite',
        'core.MicrositePage',
    ]
    subpage_types = ['core.MicrositePage']

    class Meta:
        verbose_name = _('Campaign site page')
        verbose_name_plural = _('Campaign site pages')

    page_title = models.TextField(null=True, verbose_name=_('Page title'))
    page_subheading = models.TextField(
        blank=True,
        help_text=_('This is a subheading that displays below the main title on the microsite page'),
        verbose_name=_('Page subheading'),
    )
    page_teaser = models.TextField(
        blank=True,
        null=True,
        help_text=_('This is a subheading that displays when the microsite is featured on another page'),
        verbose_name=_('Page teaser'),
    )

    use_domestic_header_logo = models.BooleanField(
        default=True,
        help_text=_(
            'If selected the dbt logo will be displayed in the header.'
            ' Otherwise the UK Gov logo will be shown. '
            'Note this checkbox only works on the root page'
        ),
        verbose_name=_('Use domestic header logo'),
    )

    external_link_label = models.CharField(
        default='',
        help_text=_('The label to be included within the menu items.'),
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_('External link label'),
    )

    external_link_url = models.URLField(
        help_text=_('The url of the external link'), blank=True, null=True, verbose_name=_('External link url')
    )

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Hero image'),
    )

    page_body = StreamField(
        [
            (
                'text',
                RichTextBlock(
                    template='microsites/blocks/text.html',
                    label=_('Text'),
                    help_text=_('Note: any indent seen here will not be visible in the live page'),
                ),
            ),
            ('image', ImageChooserBlock(required=False, template='microsites/blocks/image.html', label=_('Image'))),
            (
                'image_full_width',
                ImageChooserBlock(
                    required=False, template='microsites/blocks/image_full_width.html', label=_('Image full width')
                ),
            ),
            ('video', core_blocks.SimpleVideoBlock(template='microsites/blocks/video.html', label=_('Video'))),
            (
                'columns',
                StreamBlock(
                    [
                        ('column', MicrositeColumnBlock()),
                    ],
                    help_text=_('Add between 2 and 4 columns of text'),
                    min_num=2,
                    max_num=4,
                    template='microsites/blocks/columns.html',
                    label=_('Columns'),
                    icon='grip',
                ),
            ),
            ('links_block', LinkBlockWithHeading(template='microsites/blocks/link.html', label=_('Links block'))),
            (
                'cta',
                blocks.StructBlock(
                    [
                        (
                            'title',
                            blocks.CharBlock(required=True, max_length=255, label=_('Title')),
                        ),
                        (
                            'teaser',
                            blocks.RichTextBlock(
                                template='microsites/blocks/text.html',
                                label=_('Teaser'),
                                help_text=_('Note: any indent seen here will not be visible in the live page'),
                            ),
                        ),
                        (
                            'link_label',
                            blocks.CharBlock(required=True, max_length=255, label=_('Link label')),
                        ),
                        (
                            'link',
                            blocks.CharBlock(required=True, max_length=255, label=_('Link')),
                        ),
                    ],
                    template='microsites/blocks/cta.html',
                    label=_('CTA'),
                    icon='crosshairs',
                ),
            ),
            (  # alt text lives on the custom Image class
                'pull_quote',
                core_blocks.PullQuoteBlock(template='domestic/blocks/pull_quote_block.html', label=_('Pull quote')),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        verbose_name=_('Page body'),
    )

    cta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CTA title'),
    )
    cta_teaser = RichTextField(
        null=True,
        blank=True,
        verbose_name=_('CTA teaser'),
        help_text=_('Note: any indent seen here will not be visible in the live page'),
    )

    cta_link_label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CTA link label'),
    )
    cta_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CTA link'),
    )

    related_links = StreamField(
        [
            (
                'page',
                blocks.PageChooserBlock(null=True, blank=True, label=_('Page')),
            ),
            (
                'link',
                blocks.StructBlock(
                    [
                        (
                            'title',
                            blocks.CharBlock(form_classname='title', default='', label=_('Title')),
                        ),
                        (
                            'full_url',
                            blocks.URLBlock(form_classname='url', default='', label=_('Full url')),
                        ),
                    ],
                    label=_('Link'),
                ),
            ),
        ],
        use_json_field=True,
        max_num=5,
        null=True,
        blank=True,
    )

    twitter = models.URLField(blank=True, verbose_name=_('Twitter'))
    facebook = models.URLField(blank=True, verbose_name=_('Facebook'))
    linkedin = models.URLField(blank=True, verbose_name=_('LinkedIn'))

    def get_parent_page(self):
        current_page = self.specific
        parent_page = self.get_parent().specific
        while type(parent_page) is not Microsite:
            if type(parent_page) is not MicrositePage:
                break
            current_page = parent_page
            parent_page = parent_page.get_parent().specific
        if type(parent_page) is Microsite and type(current_page) is MicrositePage:
            return current_page
        else:
            return None

    # Return the children of the top level Microsite parent of current page
    def get_menu_items(self):
        parent_page = self.get_parent_page()
        menu_items = []
        if parent_page:
            menu_items = [{'url': parent_page.get_url(), 'title': _('Home')}] + [
                {
                    'url': child.get_url(),
                    'title': child.title,
                }
                for child in parent_page.get_children().live()
            ]
        return menu_items + self.get_external_menu_link()

    def get_use_domestic_header_logo(self):
        parent_page = self.get_parent_page()
        if parent_page and type(parent_page.specific) is MicrositePage:
            return parent_page.specific.use_domestic_header_logo
        else:
            return False

    # Return the children of a child or grandchild page
    def get_related_pages(self):
        return [{'title': child.title, 'url': child.get_url()} for child in self.get_children()]

    def get_site_title(self):
        parent_page = self.get_parent_page()
        if parent_page:
            return parent_page.title
        else:
            return None

    def get_external_menu_link(self):
        parent = self.get_parent_page()
        if parent.external_link_label and parent.external_link_url:
            return [{'url': parent.external_link_url, 'title': parent.external_link_label}]

        return []


@register_snippet
class HeroSnippet(NonPageContentSnippetBase, NonPageContentSEOMixin):
    # Provide the options for pages which will use a hero snippet
    slug_options = {
        snippet_slugs.EXPORT_ACADEMY_LISTING_PAGE_HERO: {
            'title': 'Hero for the Export Academy listing page',
            'page_path': '/export_academy/events/',
        },
        snippet_slugs.EA_REGISTRATION_PAGE_HERO: {
            'title': 'Hero for the Export Academy registration page',
            'page_path': '/export-academy/registration/',
        },
    }
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    logged_out_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    logged_in_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    ea_registered_text = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
    )
    panels = [
        MultiFieldPanel(
            heading='Purpose',
            children=[
                FieldPanel('slug', widget=Select),
            ],
        ),
        FieldPanel('title'),
        FieldPanel('text'),
        FieldPanel('image'),
        MultiFieldPanel(
            heading='Logged in, logged out and EA registered CTA text (Optional)',
            children=[
                FieldPanel('logged_out_text'),
                FieldPanel('logged_in_text'),
                FieldPanel('ea_registered_text'),
            ],
        ),
    ]


class Support(Page):
    folder_page = True
    settings_panels = [FieldPanel('slug')]

    parent_page_types = [
        'domestic.DomesticHomePage',
        'domestic.GreatDomesticHomePage',
    ]

    subpage_types = ['core.SupportPage', 'core.GetInTouchPage', 'core.SupportTopicLandingPage']

    class Meta:
        verbose_name = 'Support'
        verbose_name_plural = 'Support'

    def serve_preview(self, request, mode_name='dummy'):
        # It doesn't matter what is passed as mode_name - we always HTTP404
        raise Http404()

    def serve(self, request):
        raise Http404()


class SupportPage(cms_panels.SupportPanels, Page):
    template = 'domestic/contact/export-support/support.html'
    parent_page_types = [
        'core.Support',
        'core.SupportPage',
    ]
    subpage_types = ['core.SupportPage']

    class Meta:
        verbose_name = 'Support page'
        verbose_name_plural = 'Support pages'

    page_title = models.TextField(
        null=True,
    )
    page_teaser = RichTextField(
        blank=True,
        null=True,
    )
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    page_body = StreamField(
        [
            (
                'topic_cards',
                StreamBlock(
                    [
                        ('topic_card', SupportTopicCardBlock()),
                    ],
                    block_counts={
                        'topic_card': {'min_num': 1},
                    },
                ),
            ),
            (
                'sidebar_items',
                StreamBlock(
                    [
                        ('sidebar_item', SupportCardBlock()),
                    ],
                    block_counts={
                        'sidebar_item': {'min_num': 1},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )


class SupportTopicLandingPage(cms_panels.SupportTopicLandingPanels, Page):
    template = 'domestic/contact/export-support/topic-landing.html'
    parent_page_types = [
        'core.Support',
        'core.SupportPage',
    ]
    subpage_types = ['core.SupportPage']

    class Meta:
        verbose_name = 'Topic landing page'
        verbose_name_plural = 'Topic landing pages'

    page_title = models.TextField(
        null=True,
    )
    page_body = StreamField(
        [
            (
                'cards',
                StreamBlock(
                    [
                        ('card', SupportCardBlock()),
                        ('sidebar_item', SupportCardBlock()),
                        ('related_item', SupportCardBlock()),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )


class GetInTouchPage(cms_panels.GetInTouchPanels, Page):
    template = 'domestic/contact/export-support/get-in-touch.html'
    parent_page_types = [
        'core.Support',
        'core.SupportPage',
    ]
    subpage_types = ['core.SupportPage']

    class Meta:
        verbose_name = 'Get in touch page'
        verbose_name_plural = 'Get in touch pages'

    page_title = models.TextField(
        null=True,
    )
    page_teaser = models.TextField(
        blank=True,
        null=True,
    )
    page_body = StreamField(
        [
            (
                'cards',
                StreamBlock(
                    [
                        ('card', SupportCardBlock()),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )
