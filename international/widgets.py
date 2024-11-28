from wagtail import blocks


class SectorBlock(blocks.StructBlock):
    sectors = blocks.ListBlock(blocks.ChoiceBlock(choices=[], required=False))  # Choices will be populated by the form

    class Meta:
        template = 'international/includes/blocks/sector_block.html'
