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
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        pass


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()
