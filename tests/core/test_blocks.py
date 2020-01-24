from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from core import blocks as core_blocks


def test_image_base_block():
    assert issubclass(core_blocks.ImageBaseBlock, blocks.StructBlock)
    declared_blocks = core_blocks.ImageBaseBlock.declared_blocks
    assert declared_blocks['image'].__class__ == ImageChooserBlock
    assert declared_blocks['alt_text'].__class__ == blocks.CharBlock


def test_link_block():
    assert issubclass(core_blocks.LinkBlock, blocks.StructBlock)
    declared_blocks = core_blocks.LinkBlock.declared_blocks
    assert declared_blocks['text'].__class__ == blocks.CharBlock
    assert declared_blocks['url'].__class__ == blocks.CharBlock


def test_hero_block():
    assert issubclass(core_blocks.HeroBlock, (core_blocks.ImageBaseBlock, core_blocks.LinkBlock))
    declared_blocks = core_blocks.HeroBlock.declared_blocks
    assert declared_blocks['text'].__class__ == blocks.RichTextBlock


def test_link_with_source_block():
    assert issubclass(core_blocks.LinkWitSourceBlock, core_blocks.LinkBlock)
    declared_blocks = core_blocks.LinkWitSourceBlock.declared_blocks
    assert declared_blocks['source'].__class__ == blocks.CharBlock


def test_link_with_image_and_content_block():
    assert issubclass(
        core_blocks.LinkWithImageAndContentBlock,
        (core_blocks.ImageBaseBlock, core_blocks.LinkWitSourceBlock)
    )
    declared_blocks = core_blocks.LinkWithImageAndContentBlock.declared_blocks
    assert declared_blocks['content'].__class__ == blocks.RichTextBlock
