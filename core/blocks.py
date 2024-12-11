import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from opensearchpy.exceptions import ConnectionError, NotFoundError
from wagtail import blocks
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlockValidationError
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.telepath import register
from wagtailmedia.blocks import AbstractMediaChooserBlock

from core import models
from core.case_study_index import search
from core.constants import (
    CAMPAIGN_FORM_CHOICES,
    RICHTEXT_FEATURES__MINIMAL,
    RICHTEXT_FEATURES__REDUCED,
    RICHTEXT_FEATURES__WITH_LIST,
)
from core.utils import get_cs_ranking, get_personalised_choices

logger = logging.getLogger(__name__)


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        raise NotImplementedError("MediaChooserBlock Shouldn't be used it's own")


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()

    class Meta:
        icon = 'play'


class Item(blocks.StructBlock):
    item = blocks.CharBlock(max_length=255)


class LessonPlaceholderBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)

    class Meta:
        help_text = 'Placeholder block for a lesson which will be shown as "Coming Soon"'
        icon = 'expand'
        template = 'learn/_lesson_placeholder.html'


class LinkStructValue(blocks.StructValue):
    """
    Generates a URL for blocks with multiple link choices.
    """

    @property
    def url(self):
        page = self.get('internal_link')
        ext = self.get('external_link')
        if page:
            return page.url_path
        else:
            return ext


class LinkBlock(blocks.StructBlock):
    internal_link = blocks.PageChooserBlock(
        required=False,
        label='Internal link',
    )
    external_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label='External link',
    )

    class Meta:
        value_class = LinkStructValue
        icon = 'redirect'


class TitleBlock(blocks.CharBlock):
    class Meta:
        max_length = 255
        help_text = 'Enter a title'
        template = 'core/includes/_title.html'
        icon = 'bold'


class HrBlock(blocks.StaticBlock):
    # A horizontal full-width line
    class Meta:
        help_text = 'Horizontal rule'
        template = 'core/includes/_hr.html'
        icon = 'horizontalrule'


class ImageBlock(ImageChooserBlock):
    class Meta:
        help_text = 'Include an image'
        template = 'core/includes/_image.html'
        icon = 'image'


class SimpleVideoBlock(blocks.StructBlock):
    video = MediaChooserBlock(label=_('Video'))

    class Meta:
        help_text = _('Include a video')
        template = 'core/includes/_video.html'
        icon = 'media'


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    link = LinkBlock(required=False)
    secondary = blocks.BooleanBlock(
        required=False, help_text='Determines the appearance of the button. Default is primary.'
    )
    chevron = blocks.BooleanBlock(required=False, help_text='Adds a right chevron to the button. Default is None.')

    class Meta:
        template = 'core/button.html'
        icon = 'radio-full'


class RouteSectionBlock(blocks.StructBlock):
    # One of the three intro blocks at the top of the domestic dashboard
    route_type = blocks.ChoiceBlock(
        choices=[
            ('learn', 'Learning'),
            ('plan', 'Export plan'),
            ('target', 'Target market'),
        ],
        icon='redirect',
    )
    title = blocks.CharBlock(max_length=255)
    body = blocks.TextBlock(max_length=4096)
    image = ImageChooserBlock()
    button = ButtonBlock(icon='cog', required=False)

    class Meta:
        help_text = 'The routing block at the top of the dashboard. There should be three - learn, target, plan'
        template = 'core/includes/_route-section.html'
        icon = 'redirect'


class SidebarLinkBlock(blocks.StructBlock):
    # a link to a learning page in the RH column
    link = LinkBlock(required=True)
    title_override = blocks.CharBlock(max_length=255, required=False)
    lede_override = blocks.CharBlock(max_length=255, required=False)

    def render(self, value, context={}):
        try:
            internal_link = value['link']['internal_link']
            value['target_lede'] = internal_link.get_parent() and internal_link.get_parent().title
            value['target_title'] = internal_link.title
            # If it's a detail page, get the read duration
            if isinstance(internal_link.specific, models.DetailPage):
                detail_page = internal_link.specific.__class__.objects.get(id=internal_link.id)
                value['read_time'] = getattr(detail_page, 'estimated_read_duration')
        except (ObjectDoesNotExist, KeyError, TypeError, AttributeError):
            pass

        return super().render(value, context=context)

    class Meta:
        help_text = 'A floating link in a section to the right of the content. Labels can be overridden.'
        template = 'core/includes/_sidebar-link.html'
        icon = 'tag'


class ComponentTargetTable(blocks.StaticBlock):
    # This is a dummy block to show the principal of components
    class Meta:
        help_text = 'Target section table for marketing approach page'
        template = 'core/includes/_target_table.html'
        icon = 'grip'


class SectionBlock(blocks.StreamBlock):
    # a section in generic layout 1:2 columns
    title = TitleBlock()
    text_block = blocks.RichTextBlock(icon='openquote', helptext='Add a textblock')
    image = ImageBlock()
    hr = HrBlock()
    #  Components
    side_link = SidebarLinkBlock()
    target_table = ComponentTargetTable()

    class Meta:
        help_text = 'A 1:2 column section'
        template = 'core/includes/_section.html'
        icon = 'placeholder'


class ModularContentStaticBlock(blocks.StaticBlock):
    class Meta:
        admin_text = 'Content modules will be automatically displayed, no configuration needed.'
        icon = 'archive'
        template = 'core/cs_block.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if 'tags' in context['request'].GET:
            from core.models import ContentModule

            tags = context['request'].GET['tags'].split(',')
            context['modules'] = ContentModule.objects.filter(tags__name__in=tags).distinct()
        return context


class StepByStepBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    body = blocks.RichTextBlock()
    image = ImageChooserBlock(required=False)

    class Meta:
        template = 'learn/step_by_step.html'


class ITAQuoteBlock(blocks.StructBlock):
    quote = blocks.RichTextBlock()
    author = blocks.CharBlock(max_length=255)

    class Meta:
        template = 'learn/ita_quote.html'


class ChooseDoNotChooseBlock(blocks.StructBlock):
    choose_title = blocks.CharBlock(max_length=255)
    choose_body = blocks.RichTextBlock(features=RICHTEXT_FEATURES__WITH_LIST)

    do_not_choose_title = blocks.CharBlock(max_length=255)
    do_not_choose_body = blocks.RichTextBlock(features=RICHTEXT_FEATURES__WITH_LIST)

    class Meta:
        help_text = 'A pair of custom rich-text areas with titles, one for Choose and the other for Do Not Choose'
        icon = 'question-circle'
        template = 'learn/choose_do_not_choose.html'


class CaseStudyStaticBlock(blocks.StaticBlock):
    class Meta:
        admin_text = (
            'Case Studies are automatically displayed based on '
            'personalisation rules; no configuration needed beyond '
            'adding this block to the page.'
        )
        icon = 'book'
        template = 'core/case_study_block.html'

    def _get_case_study_list(self, user, cs_settings, page_context):
        export_commodity_codes, export_markets, export_regions, export_blocs = get_personalised_choices(user)

        try:
            s = search(
                export_commodity_codes=export_commodity_codes,
                export_markets=export_markets,
                export_regions=export_regions,
                page_context=page_context,
            )
            if s.count():
                hits = []
                for hit in s.scan():
                    hit_dict = hit.to_dict()
                    hit_dict['score'] = get_cs_ranking(
                        hit_dict,
                        export_commodity_codes=export_commodity_codes,
                        export_markets=export_markets,
                        export_regions=export_regions,
                        page_context=page_context,
                        export_blocs=export_blocs,
                        settings=cs_settings,
                    )
                    hits.append(hit_dict)
                return sorted(hits, key=lambda hit: hit.get('score'), reverse=True)

        except ConnectionError:
            # nothing we can do without opensearch so continue without case study
            logger.error('Unable to connect to Elastic search')
        except NotFoundError:
            logger.error(f'Elastic search - Index "{settings.OPENSEARCH_CASE_STUDY_INDEX}" not found')

    def _annotate_with_case_study(self, context):
        """Add the most relevant case study, if any, to the context."""

        # Get the context for this lesson -> module -> topic
        page_context = []
        for page_type in ['lesson', 'module', 'topic']:
            page = context.get(f'current_{page_type}')
            page_context.append(f'{page_type}_{page.id if page else ""}')

        # Get the user's basket products and markets
        user = context.get('user')
        from core.models import CaseStudyScoringSettings

        cs_settings = CaseStudyScoringSettings.for_request(context['request'])
        case_study_list = self._get_case_study_list(user, cs_settings, page_context)
        best_case_study = case_study_list and case_study_list[0]
        try:
            if best_case_study and int(best_case_study.get('score')) >= cs_settings.threshold:
                context['case_study'] = models.CaseStudy.objects.get(id=best_case_study.get('pk'))
            if case_study_list and settings.FEATURE_SHOW_CASE_STUDY_RANKINGS:
                context['feature_show_case_study_list'] = True
                context['case_study_list'] = [
                    {
                        'pk': cs.get('pk'),
                        'title': models.CaseStudy.objects.get(id=cs.get('pk')).lead_title,
                        'score': cs.get('score'),
                        'above_threshold': cs.get('score') >= cs_settings.threshold,
                    }
                    for cs in case_study_list
                ]
        except models.CaseStudy.DoesNotExist:
            # The case study does not exist in the DB mismatch between elastic search and DB.
            # Rebuild Elastic search case-studies using management command
            logger.error('No case-study not found in the database using ID in elastic search')
        return context

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = self._annotate_with_case_study(context)
        return context


class CaseStudyQuoteBlock(blocks.StructBlock):
    quotes = blocks.StreamBlock(
        [
            (
                'quote',
                blocks.RichTextBlock(
                    features=RICHTEXT_FEATURES__MINIMAL,
                ),
            )
        ],
        block_counts={'quote': {'max_num': 10}},
        required=False,
    )
    attribution = blocks.CharBlock(
        max_length=255,
        label='Who said it?',
        required=False,
    )
    role = blocks.CharBlock(
        max_length=255,
        label='Their role',
        required=False,
    )

    class Meta:
        icon = 'quote-left'
        template = 'core/includes/_case_study_quote_block.html'


def general_statistics_streamfield_validation(value):
    if value and (len(value) < 2 or len(value) > 6):
        raise StreamBlockValidationError(
            non_block_errors=ValidationError(
                'There must be between two and six statistics in this panel', code='invalid'
            ),
        )


class IndividualStatisticBlock(blocks.StructBlock):
    """Stores an individual statistic"""

    number = blocks.CharBlock(max_length=255)
    heading = blocks.CharBlock(max_length=255)
    smallprint = blocks.CharBlock(max_length=255, required=False)


class IndividualStatisticBlockAdaptor(StructBlockAdapter):
    js_constructor = 'core.blocks.IndividualStatisticBlock'

    @cached_property
    def media(self):
        structblock_media = super().media
        return forms.Media(
            js=structblock_media._js + ['javascript/individualstatistic-block.js'], css=structblock_media._css
        )


register(IndividualStatisticBlockAdaptor(), IndividualStatisticBlock)


class CountryGuideIndustrySubsectionBlock(blocks.StructBlock):
    icon = ImageChooserBlock(required=False, label='Subsection icon')
    heading = blocks.CharBlock(max_length=255, label='Subsection heading')
    body = blocks.TextBlock(required=False, label='Subsection body')


class CountryGuideCaseStudyBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=255, label='Case study title')
    hero_image = ImageChooserBlock(required=False, label='Case study hero image')
    description = blocks.TextBlock(required=False, label='Case study description')
    button_text = blocks.CharBlock(required=False, max_length=255, label='Case study button text')
    button_link = blocks.URLBlock(required=False, label='Case study button link')


class CountryGuideIndustryBlock(blocks.StructBlock):
    # Replacing a large set of fields each set of which was repeated six
    # times in V1's CountryGuidePage model as `accordion_*``

    icon = ImageChooserBlock(required=False, label='Industry icon')
    title = blocks.CharBlock(max_length=255, label='Industry title')
    teaser = blocks.TextBlock(required=False, label='Industry teaser')

    subsections = blocks.StreamBlock(
        [('subsection', CountryGuideIndustrySubsectionBlock())],
        block_counts={'subsection': {'max_num': 3}},
        required=False,
    )

    statistics = blocks.StreamBlock(
        [
            (
                'statistic',
                IndividualStatisticBlock(
                    icon='calculator',
                    required=False,
                ),
            )
        ],
        null=True,
        blank=True,
        required=False,
        validators=[general_statistics_streamfield_validation],
    )

    case_study = CountryGuideCaseStudyBlock(required=False)

    class Meta:
        template = 'domestic/includes/blocks/accordions.html'


class CountryGuideIndustryLinkBlock(blocks.StructBlock):

    icon = ImageChooserBlock(required=False, label='Industry icon')
    title = blocks.CharBlock(max_length=255, label='Industry title')
    page = blocks.PageChooserBlock(label='Page')

    class Meta:
        template = 'domestic/includes/blocks/sector_link.html'


class PullQuoteBlock(blocks.StructBlock):
    # Note: this does not have a default template; we can add one when
    # there is a single standard style for all of Magna

    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(
        max_length=255,
        label='Who said it?',
        required=False,
    )
    role = blocks.CharBlock(
        max_length=255,
        label='Their role',
        required=False,
    )
    organisation = blocks.CharBlock(
        max_length=255,
        label='Their organisation',
        required=False,
    )
    organisation_link = blocks.URLBlock(
        max_length=255,
        label='Link to organisation site',
        required=False,
    )

    class Meta:
        icon = 'openquote'


class PerformanceDashboardDataBlock(blocks.StructBlock):
    data_title = blocks.CharBlock(max_length=100)
    data_value = blocks.CharBlock(max_length=100)
    data_period = blocks.CharBlock(max_length=100)
    data_description = blocks.RichTextBlock(
        features=RICHTEXT_FEATURES__REDUCED,
    )

    class Meta:
        template = 'domestic/blocks/performance_dash_data_block.html'


class LinkWithImageAndContentBlock(blocks.StructBlock):
    source = blocks.CharBlock(help_text='The source or the type of the link, e.g. GOV.UK/Advice')
    text = blocks.CharBlock()
    url = blocks.CharBlock()  # not a URL block to allow relative links
    image = ImageChooserBlock(required=False)  # alt text lives on the custom Image class
    content = blocks.RichTextBlock()


class LinkWithImageAndContentBlockNoSource(blocks.StructBlock):
    text = blocks.CharBlock()
    url = blocks.CharBlock()  # not a URL block to allow relative links
    image = ImageChooserBlock(required=False)  # alt text lives on the custom Image class
    content = blocks.RichTextBlock(
        features=RICHTEXT_FEATURES__REDUCED,
    )


class SliceBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    url = blocks.CharBlock()
    source = blocks.CharBlock(help_text='The source or the type of the link, e.g. GOV.UK/Advice', required=False)
    image = ImageChooserBlock()
    summary = blocks.RichTextBlock(features=RICHTEXT_FEATURES__REDUCED, required=False)


class VideoChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """We don't need any HTML rendering"""
        if not value:
            return ''
        return value.file.url


class CampaignBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    subheading = blocks.CharBlock()
    related_link_text = blocks.CharBlock()
    related_link_url = blocks.CharBlock()
    image = ImageChooserBlock()
    video = VideoChooserBlock()

    class Meta:
        icon = 'media'


class AdvantageBlock(blocks.StructBlock):
    icon = ImageChooserBlock()
    content = RichTextBlock(features=RICHTEXT_FEATURES__REDUCED)

    class Meta:
        icon = 'plus'


class TopicPageCardBlock(blocks.StructBlock):
    """Used in ManuallyConfigurableTopicPage"""

    link_text = blocks.CharBlock()
    link_url = blocks.CharBlock()  # not a URL block to allow relative links
    image = ImageChooserBlock(required=False)  # alt text lives on the custom Image class
    description = blocks.TextBlock()


class ColumnsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=255, label='Title')
    image = ImageChooserBlock(required=False, label='Hero Image')
    description = blocks.RichTextBlock(features=RICHTEXT_FEATURES__REDUCED, required=False, label='Description')
    link = blocks.URLBlock(required=False, label='Title link')


class MicrositeColumnBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False, label=_('Hero image'))
    image_url = blocks.URLBlock(required=False, label=_('Hero image hyperlink'))
    text = blocks.RichTextBlock(
        required=False,
        label=_('Description'),
        help_text=_('Note: any indent seen here will not be visible in the live page'),
    )
    button_label = blocks.CharBlock(required=False, label=_('Button label'))
    button_url = blocks.URLBlock(required=False, label=_('Button url'))


class SingleRichTextBlock(blocks.StructBlock):
    description = blocks.RichTextBlock(features=RICHTEXT_FEATURES__REDUCED, required=False, label='Description')


class TopicPageCardBlockRichText(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=255, label='Title')
    image = ImageChooserBlock(required=False, label='Hero Image')
    description = blocks.RichTextBlock(features=RICHTEXT_FEATURES__REDUCED, required=False, label='Description')
    link = blocks.CharBlock()  # not a URL block to allow relative links


class LinksBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, max_length=255, label=_('Title'))
    description = blocks.RichTextBlock(features=RICHTEXT_FEATURES__REDUCED, required=False, label=_('Description'))
    link_text = blocks.CharBlock(label=_('Link text'))
    link_url = blocks.URLBlock(label=_('Link url'))

    class Meta:
        icon = 'link'


class LinkBlockWithHeading(blocks.StructBlock):
    text = blocks.RichTextBlock(required=False, label='Text (optional)')
    links = blocks.StreamBlock([('link', LinksBlock(label=_('Link block')))], max_num=6, required=True)

    class Meta:
        icon = 'link'


class CampaignFormBlock(blocks.StructBlock):
    type = blocks.ChoiceBlock(choices=CAMPAIGN_FORM_CHOICES, null=False, blank=False, required=True, label=_('type'))
    email_subject = blocks.TextBlock(required=True, label=_('Email subject'))
    email_title = blocks.TextBlock(required=True, label=_('Email title'))
    email_body = blocks.TextBlock(required=True, label=_('Email body'))

    class Meta:
        icon = 'form'


class SupportCardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False, label=_('Card Image'))
    type = blocks.ChoiceBlock(
        choices=[
            ('govuk', _('GOV.UK')),
            ('tool', _('Tool')),
            ('howTo', _('How to')),
            ('service', _('Service')),
        ],
        label=_('Type'),
        required=False,
    )
    title = blocks.CharBlock(max_length=255, label=_('Title'))
    description = blocks.CharBlock(max_length=255, label=_('Description'))
    link_text = blocks.CharBlock(label=_('Link text'))
    link_url = blocks.CharBlock(label=_('Link url'))
    full_width = blocks.ChoiceBlock(
        choices=[('yes', _('Yes')), ('no', _('No'))], label=_('Full width?'), required=False
    )


class SupportTopicCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, label=_('Title'))
    description = blocks.CharBlock(required=False, max_length=255, label=_('Description'))
    link_text = blocks.CharBlock(required=False, label=_('Link text'))
    link_url = blocks.CharBlock(label=_('Link url'))


class SupportHomepageCardBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(label=_('Link text'))
    link_url = blocks.CharBlock(label=_('Link url'))


class BasicTopicCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, label=_('Title'))
    description = blocks.CharBlock(required=False, max_length=255, label=_('Description'))


class DataTableBlock(TableBlock):
    """A simple table block"""

    class Meta:
        template = 'core/table.html'


class ArticleListingLinkBlock(blocks.StructBlock):
    link_text = blocks.CharBlock(max_length=255, label='Link text')
    link_page = blocks.PageChooserBlock(page_type='domestic.ArticlePage', label='Choose article page')
