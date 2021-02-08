from django.core.exceptions import ObjectDoesNotExist, ValidationError
from wagtail.core import blocks
from wagtail.core.blocks.stream_block import StreamBlockValidationError
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock

from core import models
from core.constants import RICHTEXT_FEATURES__MINIMAL, RICHTEXT_FEATURES__REDUCED
from core.utils import (
    get_personalised_case_study_orm_filter_args,
    get_personalised_choices,
)


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        raise NotImplementedError("MediaChooserBlock Shouldn't be used it's own")


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()

    class Meta:
        icon = 'fa-play'


class Item(blocks.StructBlock):
    item = blocks.CharBlock(max_length=255)


class LessonPlaceholderBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)

    class Meta:
        help_text = 'Placeholder block for a lesson which will be shown as "Coming Soon"'
        icon = 'fa-expand'
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
    video = MediaChooserBlock()

    class Meta:
        help_text = 'Include a video'
        template = 'core/includes/_video.html'
        icon = 'fa-play'


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    link = LinkBlock(required=False)

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
        icon = 'fa-archive'
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
    choose_body = blocks.RichTextBlock(features=RICHTEXT_FEATURES__MINIMAL)

    do_not_choose_title = blocks.CharBlock(max_length=255)
    do_not_choose_body = blocks.RichTextBlock(features=RICHTEXT_FEATURES__MINIMAL)

    class Meta:
        help_text = 'A pair of custom rich-text areas with titles, one for Choose and the other for Do Not Choose'
        icon = 'fa-question-circle'
        template = 'learn/choose_do_not_choose.html'


class CaseStudyStaticBlock(blocks.StaticBlock):
    class Meta:
        admin_text = (
            'Case Studies are automatically displayed based on '
            'personalisation rules; no configuration needed beyond '
            'adding this block to the page.'
        )
        icon = 'fa-book'
        template = 'core/case_study_block.html'

    def _annotate_with_case_study(self, context):
        """Add the relevant case study, if any, to the context."""

        # no export_plan no case_study to display
        if 'export_plan' not in context.keys():
            return context

        hs_code, country, region = get_personalised_choices(context['export_plan'])

        filter_args = get_personalised_case_study_orm_filter_args(hs_code=hs_code, country=country, region=region)
        queryset = models.CaseStudy.objects.all()
        for filter_arg in filter_args:
            case_study = queryset.filter(**filter_arg)
            if case_study.exists():
                context['case_study'] = case_study.distinct().latest()
                break

        return context

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context = self._annotate_with_case_study(context)
        return context


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
                    icon='fa-calculator',
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
        template = 'domestic/content/blocks/accordions.html'


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
        icon = 'fa-quote-left'


class PerformanceDashboardDataBlock(blocks.StructBlock):

    data_title = blocks.CharBlock(max_length=100)
    data_value = blocks.CharBlock(max_length=100)
    data_period = blocks.CharBlock(max_length=100)
    data_description = blocks.RichTextBlock(
        features=RICHTEXT_FEATURES__REDUCED,
    )

    class Meta:
        template = 'domestic/blocks/performance_dash_data_block.html'
