from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from wagtail.core import blocks
from wagtailmedia.blocks import AbstractMediaChooserBlock


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        pass


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
            return page.url
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


class ModularContentStaticBlock(blocks.StaticBlock):

    class Meta:
        admin_text = 'Content modules will be automatically displayed, no configuration needed.'
        icon = 'fa-archive'

    def render_basic(self, value, context=None):
        html = ''
        if 'tags' in context['request'].GET:
            from core.models import ContentModule

            tags = context['request'].GET['tags'].split(',')
            modules = ContentModule.objects.filter(tags__name__in=tags).distinct()
            div = '<div class="modules"> {} </div>'
            html = format_html(
                div,
                format_html_join('\n', "<div> {} </div>", ((mark_safe(module.content),) for module in modules))
            )
        return html
