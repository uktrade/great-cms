from wagtail import blocks


class MetaDataBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    value = blocks.CharBlock(required=True)
