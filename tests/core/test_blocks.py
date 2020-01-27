from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from core import blocks as core_blocks


def test_image_base_block():
    assert issubclass(core_blocks.ImageBaseBlock, blocks.StructBlock)
    child_blocks = core_blocks.ImageBaseBlock().child_blocks
    assert type(child_blocks['image']) is ImageChooserBlock
    assert type(child_blocks['alt_text']) is blocks.CharBlock


def test_link_block():
    assert issubclass(core_blocks.LinkBlock, blocks.StructBlock)
    child_blocks = core_blocks.LinkBlock().child_blocks
    assert type(child_blocks['text']) is blocks.CharBlock
    assert type(child_blocks['url']) is blocks.CharBlock


def test_hero_block():
    assert issubclass(core_blocks.HeroBlock, (core_blocks.ImageBaseBlock, core_blocks.LinkBlock))
    child_blocks = core_blocks.HeroBlock().child_blocks
    assert type(child_blocks['text']) is blocks.RichTextBlock


def test_link_with_source_block():
    assert issubclass(core_blocks.LinkWitSourceBlock, core_blocks.LinkBlock)
    child_blocks = core_blocks.LinkWitSourceBlock().child_blocks
    assert type(child_blocks['source']) is blocks.CharBlock


def test_link_with_image_and_content_block():
    assert issubclass(
        core_blocks.LinkWithImageAndContentBlock,
        (core_blocks.ImageBaseBlock, core_blocks.LinkWitSourceBlock)
    )
    child_blocks = core_blocks.LinkWithImageAndContentBlock().child_blocks
    assert type(child_blocks['content']) is blocks.RichTextBlock
