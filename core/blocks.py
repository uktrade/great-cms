from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        raise NotImplementedError("MediaChooserBlock Shouldn't be used it's own")


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()


class CuratedTopicBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    pages = blocks.ListBlock(blocks.PageChooserBlock(label='Detail page'))

    class Meta:
        template = 'core/curated_topic.html'


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


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    link = LinkBlock(required=False)

    class Meta:
        template = 'core/button.html'


class RouteSectionBlock(blocks.StructBlock):
    route_type = blocks.ChoiceBlock(choices=[
        ('learn', 'Learning'),
        ('plan', 'Export plan'),
        ('target', 'Target market'),
    ], icon='redirect')
    title = blocks.CharBlock(max_length=255)
    body = blocks.TextBlock(max_length=4096)
    image = ImageChooserBlock()
    button = ButtonBlock(icon='cog', required=False)

    class Meta:
        admin_text = 'The routing block at the top of the dashboard. There should be three - learn, target, plan'
        template = 'core/includes/_route-section.html'


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
