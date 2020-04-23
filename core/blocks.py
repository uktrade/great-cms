from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=255, required=False)
    url = blocks.CharBlock(max_length=255, required=False)  # not a URL block to allow relative links


class HeroBlock(LinkBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()


class LinkWithSourceBlock(LinkBlock):
    source = blocks.CharBlock(help_text='The source or the type of the link, e.g. GOV.UK/Advice')


class LinkWithImageAndContentBlock(LinkWithSourceBlock):
    content = blocks.RichTextBlock()
    image = ImageChooserBlock()


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''
        return value.file.url


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()

    def render(self, value, context=None):
        if not value:
            return ''
        sources = format_html_join('\n', '<source{0}>', [[flatatt(source)] for source in value['video'].sources])
        return format_html(
            f"""
                    <div>
                        <video width="{value['width']}" height="{value['height']}" controls>
                            {sources}
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    """
        )
