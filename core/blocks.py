from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


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


