from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class ImageBaseBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(required=False)


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=255)
    url = blocks.CharBlock(max_length=255)  # not a URL block to allow relative links


class HeroBlock(ImageBaseBlock, LinkBlock):
    text = blocks.RichTextBlock(null=True, blank=True)


class LinkWitSourceBlock(LinkBlock):
    source = blocks.CharBlock(help_text='The source or the type of the link, e.g. GOV.UK/Advice')


class LinkWithImageAndContentBlock(LinkWitSourceBlock, ImageBaseBlock):
    content = blocks.RichTextBlock()
