from wagtail import blocks


class DomesticGrowthCardBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255, label='Title')
    description = blocks.CharBlock(required=False, max_length=255, label='Description')
    url = blocks.CharBlock(required=False, max_length=255, label='URL')
