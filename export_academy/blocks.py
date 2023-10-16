from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class MetaDataBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    value = blocks.CharBlock(required=True)


class ReviewBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    quote = blocks.TextBlock(required=True, help_text='Enter a quote (*required)')
    name = blocks.TextBlock(required=False)
    role = blocks.TextBlock(required=False)
    company_name = blocks.TextBlock(required=False)
