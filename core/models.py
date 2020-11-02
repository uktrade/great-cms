import hashlib
import mimetypes
from urllib.parse import unquote

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from modelcluster.models import ClusterableModel, ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, TagBase, ItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core import blocks
from wagtail.core.blocks.stream_block import StreamBlockValidationError
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.contrib.redirects.models import Redirect
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.snippets.models import register_snippet
from wagtail.utils.decorators import cached_classmethod
from wagtail_personalisation.blocks import PersonalisedStructBlock
from wagtail_personalisation.models import PersonalisablePageMixin
from wagtailmedia.models import Media

from core import blocks as core_blocks, mixins
from core.constants import (
    BACKLINK_QUERYSTRING_NAME,
    LESSON_BLOCK,
    RICHTEXT_FEATURES__MINIMAL
)

from core.context import get_context_provider
from core.utils import PageTopic, get_first_lesson

from great_components.mixins import GA360Mixin

from exportplan.data import SECTION_URLS as EXPORT_PLAN_SECTION_TITLES_URLS


# If we make a Redirect appear as a Snippet, we can sync it via Wagtail-Transfer
register_snippet(Redirect)


class GreatMedia(Media):

    transcript = models.TextField(
        verbose_name=_('Transcript'),
        blank=False,
        null=True  # left null because was an existing field
    )

    admin_form_fields = Media.admin_form_fields + ('transcript', )

    @property
    def sources(self):
        return [{
            'src': self.url,
            'type': mimetypes.guess_type(self.filename)[0] or 'application/octet-stream',
            'transcript': self.transcript
        }]


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

    @property
    def alt(self):
        return self.image.alt_text


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

class CMSGenericPage(
    PersonalisablePageMixin,
    mixins.EnableTourMixin,
    mixins.ExportPlanMixin,
    mixins.AuthenticatedUserRequired,
    mixins.WagtailGA360Mixin,
    GA360Mixin,
    Page
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

        return TabbedInterface(panels).bind_to(model=cls)

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
    parent_page_types = ['domestic.DomesticHomePage']
    subpage_types = ['core.ListPage', 'core.InterstitialPage',
                     'exportplan.ExportPlanDashboardPage', 'domestic.DomesticDashboard']
    template_choices = (
        ('learn/landing_page.html', 'Learn'),
        ('core/generic_page.html', 'Generic'),
    )

    ################
    # Content fields
    ################
    description = RichTextField()
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = StreamField([
        ('section', core_blocks.SectionBlock()),
        ('title', core_blocks.TitleBlock()),
        ('text', blocks.RichTextBlock(icon='openquote', helptext='Add a textblock')),
        ('image', core_blocks.ImageBlock()),
    ], null=True, blank=True)

    components = StreamField([
        ('route', core_blocks.RouteSectionBlock()),
    ], null=True, blank=True)

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('description'),
        StreamFieldPanel('button'),
        ImageChooserPanel('image'),
        StreamFieldPanel('components'),
        StreamFieldPanel('body'),
    ]


class InterstitialPage(CMSGenericPage):
    parent_page_types = ['core.LandingPage']
    template_choices = (
        ('learn/interstitial.html', 'Learn'),
    )

    ################
    # Content fields
    ################
    button = StreamField([('button', core_blocks.ButtonBlock(icon='cog'))], null=True, blank=True)

    #########
    # Panels
    #########
    content_panels = CMSGenericPage.content_panels + [
        StreamFieldPanel('button'),
    ]


class ListPage(CMSGenericPage):
    parent_page_types = ['core.LandingPage']
    subpage_types = ['core.CuratedListPage']

    template_choices = (
        ('exportplan/automated_list_page.html', 'Export plan'),
        ('learn/automated_list_page.html', 'Learn'),
    )

    record_read_progress = models.BooleanField(
        default=False,
        help_text='Should we record when a user views a page in this collection?',
    )

    class Meta:
        verbose_name = 'Automated list page'
        verbose_name_plural = 'Automated list pages'

    def get_context(self, request, *args, **kwargs):
        from domestic.helpers import get_lesson_completion_status
        from core.helpers import get_high_level_completion_progress
        context = super().get_context(request)

        if request.user.is_authenticated:
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
        'core.DetailPage',
    ]
    template_choices = (
        ('learn/curated_list_page.html', 'Learn'),
    )

    ################
    # Content fields
    ################
    heading = RichTextField()
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    topics = StreamField([('topic', core_blocks.CuratedTopicBlock(icon='plus'))], null=True, blank=True)

    ########
    # Panels
    ########
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('heading'),
        ImageChooserPanel('image'),
        StreamFieldPanel('topics')
    ]

    @cached_property
    def count_topics(self):
        return len(self.topics)

    @cached_property
    def count_detail_pages(self):
        count = 0
        for topic in self.topics:
            for lesson_or_placeholder_block in topic.value.get(
                'lessons_and_placeholders'
            ):
                if lesson_or_placeholder_block.block_type == LESSON_BLOCK:
                    count += 1
        return count

    def get_context(self, request, *args, **kwargs):
        from domestic.helpers import get_lesson_completion_status
        from core.helpers import (
            get_high_level_completion_progress,
            get_module_completion_progress
        )
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
            non_block_errors=ValidationError(
                'Only one image or video allowed in Hero section',
                code='invalid'
            ),
        )


class TopicPage(
    mixins.AuthenticatedUserRequired,
    Page
):
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

    def serve_preview(self, request):
        return self._redirect_to_parent_module()

    def serve(self, request):
        return self._redirect_to_parent_module()


class LessonPlaceholderPage(
    mixins.AuthenticatedUserRequired,
    Page
):

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

    def serve_preview(self, request):
        return self._redirect_to_parent_module()

    def serve(self, request):
        return self._redirect_to_parent_module()


class DetailPage(CMSGenericPage):
    estimated_read_duration = models.DurationField(
        null=True,
        blank=True
    )
    parent_page_types = [
        'core.CuratedListPage',  # TEMPORARY: remove after topics refactor migration has run
        'core.TopicPage'
    ]
    template_choices = (
        ('exportplan/dashboard_page.html', 'Export plan dashboard'),
        ('learn/detail_page.html', 'Learn'),
    )

    topic_block_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Detail page'
        verbose_name_plural = 'Detail pages'

    ################
    # Content fields
    ################
    hero = StreamField([
        ('Image', core_blocks.ImageBlock(template='core/includes/_hero_image.html')),
        ('Video', core_blocks.SimpleVideoBlock(template='core/includes/_hero_video.html'))],
        null=True,
        validators=[hero_singular_validation]
    )
    objective = StreamField([
        ('paragraph', blocks.RichTextBlock(options={'class': 'objectives'}),),
        ('ListItem', core_blocks.Item()),
    ])
    body = StreamField([
        (
            'paragraph', PersonalisedStructBlock(
                [('paragraph', blocks.RichTextBlock())],
                template='core/personalised_page_struct_paragraph_block.html',
                icon='fa-font'
            )
        ),
        (
            'video', PersonalisedStructBlock(
                [('video', core_blocks.VideoBlock())],
                template='core/personalised_page_struct_video_block.html',
                icon='fa-play'
            )
        ),
        (
            'case_study',
            core_blocks.CaseStudyStaticBlock(
                icon='fa-book'
            )
        ),
        ('Step', core_blocks.StepByStepBlock(icon='cog'),),
        ('fictional_example', blocks.StructBlock(
            [('fiction_body', blocks.RichTextBlock(icon='openquote'))],
            template='learn/fictional_company_example.html',
            icon='fa-commenting-o',
        ),),
        ('ITA_Quote', core_blocks.ITAQuoteBlock(icon='fa-quote-left'),),
        (
            'pros_cons',
            blocks.StructBlock(
                [
                    ('pros', blocks.StreamBlock([
                        ('item', core_blocks.Item(icon='fa-arrow-right'),)]
                    )),
                    ('cons', blocks.StreamBlock([
                        ('item', core_blocks.Item(icon='fa-arrow-right'),)]
                    ))
                ],
                template='learn/pros_and_cons.html',
                icon='fa-arrow-right',
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
    ])
    recap = StreamField([
        ('recap_item', blocks.StructBlock([
            ('title', blocks.CharBlock(icon='fa-header')),
            ('item', blocks.StreamBlock([
                ('item', core_blocks.Item(),)]
            ))
        ],
            template='learn/recap.html',
            icon='fa-commenting-o', ),)
    ])

    #########
    # Panels
    ##########
    content_panels = Page.content_panels + [
        StreamFieldPanel('hero'),
        StreamFieldPanel('objective'),
        StreamFieldPanel('body'),
        StreamFieldPanel('recap'),
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
        if self.topic_block_id:
            topic_pages = self.get_parent()
            for topic in topic_pages.specific.topics:
                if topic.id == self.topic_block_id:
                    return topic.value['title']

    @cached_property
    def module(self):
        """Gets the learning module this lesson belongs to"""
        # NB: assumes this page is a child of the correct CuratedListPage
        return self.get_parent().specific

    @cached_property
    def _export_plan_url_map(self):
        """Return a lookup dictionary of URL->title for all the
        Export Plan sections we have."""

        return {
            entry['url']: entry['title'] for entry in EXPORT_PLAN_SECTION_TITLES_URLS
        }

    def _get_backlink(self, request):
        """Try to extract a backlink (used for a link to the export plan) from the
        querystring on the request that brought us to this view.

        Only accepts backlinks that we KNOW are for the export plan, else ignore it."""
        backlink_path = request.GET.get(BACKLINK_QUERYSTRING_NAME, '')
        if backlink_path is not None:
            backlink_path = unquote(backlink_path)

            if (
                    backlink_path.split('?')[0] in self._export_plan_url_map and  # noqa:W504
                    '://' not in backlink_path
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

        if backlink_path:
            _path = backlink_path.split('?')[0]
            return self._export_plan_url_map.get(_path)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)

        # Prepare backlink to the export plan if we detect one and can validate it
        _backlink = self._get_backlink(request)
        if _backlink:
            context['backlink'] = _backlink
            context['backlink_title'] = self._get_backlink_title(_backlink)

        if hasattr(self.get_parent().specific, 'topics'):
            page_topic = PageTopic(self)
            next_lesson = page_topic.get_next_lesson()
            context['current_module'] = page_topic.module
            if page_topic and page_topic.get_page_topic():
                context['page_topic'] = page_topic.get_page_topic().value['title']

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
    _OR_ a geographical string ('Europe')
    """

    # free_tagging = False  # DISABLED until tag data only comes via data migration

    class Meta:
        verbose_name = 'Country tag for personalisation'
        verbose_name_plural = 'Country tags for personalisation'


# If you're wondering what's going on here:
# https://docs.wagtail.io/en/stable/reference/pages/model_recipes.html#custom-tag-models

class HSCodeTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationHSCodeTag,
        related_name='hscode_tagged_case_studies',
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to='core.CaseStudy',
        on_delete=models.CASCADE,
        related_name='hs_code_tagged_items'
    )


class CountryTaggedCaseStudy(ItemBase):
    tag = models.ForeignKey(
        PersonalisationCountryTag,
        related_name='country_tagged_case_studies',
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to='core.CaseStudy',
        on_delete=models.CASCADE,
        related_name='country_tagged_items'
    )


def _high_level_validation(value, error_messages):
    TEXT_BLOCK = 'text'  # noqa N806
    MEDIA_BLOCK = 'media'  # noqa N806

    # we need to be strict about presence and ordering of these nodes
    if [node.block_type for node in value] != [
        MEDIA_BLOCK, TEXT_BLOCK
    ]:
        error_messages.append(
            (
                'This block must contain one Media section (with one or '
                'two items in it), then one Text section following it.'
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
                    error_messages.append(
                        'Only one video may be used in a case study.'
                    )
                elif subnode_block_types[1] == VIDEO_BLOCK:
                    # implicitly, [0] must be an image
                    # video after image: not allowed
                    error_messages.append(
                        'The video must come before a still image.'
                    )

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
                non_block_errors=ValidationError(
                    '; '.join(error_messages),
                    code='invalid'
                ),
            )


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
    )

    company_name = models.CharField(
        max_length=255,
        blank=False,
    )
    summary = models.TextField(  # Deliberately not rich-text / no formatting
        blank=False
    )
    body = StreamField(
        [
            (
                'media',
                blocks.StreamBlock(
                    [
                        (
                            'video',
                            core_blocks.SimpleVideoBlock(
                                template='core/includes/_case_study_video.html'
                            )
                        ),
                        ('image', core_blocks.ImageBlock()),
                    ],
                    min_num=1,
                    max_num=2,
                )
            ),
            (
                'text',
                blocks.RichTextBlock(
                    features=RICHTEXT_FEATURES__MINIMAL,
                ),
            ),
        ],
        validators=[case_study_body_validation],
        help_text=(
            'This block must contain one Media section '
            '(with one or two items in it) and one Text section.'
        )
    )

    # We are keeping the personalisation-relevant tags in separate
    # fields to aid lookup and make the UX easier for editors
    hs_code_tags = ClusterTaggableManager(
        through='core.HSCodeTaggedCaseStudy',
        blank=True,
        verbose_name='HS-code tags'
    )

    country_code_tags = ClusterTaggableManager(
        through='core.CountryTaggedCaseStudy',
        blank=True,
        verbose_name='Country tags'
    )

    created = CreationDateTimeField('created', null=True)
    modified = ModificationDateTimeField('modified', null=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('company_name'),
                FieldPanel('summary'),
                StreamFieldPanel('body'),
            ],
            heading='Case Study content',
        ),
        MultiFieldPanel(
            [
                FieldPanel('hs_code_tags'),
                FieldPanel('country_code_tags')
            ],
            heading='Case Study tags for Personalisation'
        ),
    ]

    def __str__(self):
        display_name = self.title if self.title else self.company_name
        return f'{display_name}'

    def save(self, **kwargs):
        self.update_modified = kwargs.pop(
            'update_modified',
            getattr(self, 'update_modified', True)
        )
        super().save(**kwargs)

    class Meta:
        verbose_name_plural = 'Case studies'
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
