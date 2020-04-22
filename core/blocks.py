from django.utils.html import format_html
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
        return format_html(
            f"""
                    <div>
                        <video width="{self.width}" height="{self.height}" controls>
                            {source}
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    """
        )
