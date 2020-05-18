from wagtail.core import blocks

from core import blocks as core_blocks


def test_link_block():
    assert issubclass(core_blocks.LinkBlock, blocks.StructBlock)
    child_blocks = core_blocks.LinkBlock().child_blocks
    assert type(child_blocks['internal_link']) is blocks.PageChooserBlock
    assert type(child_blocks['external_link']) is blocks.CharBlock


def test_curated_topic_block():
    assert issubclass(core_blocks.CuratedTopicBlock, blocks.StructBlock)
    child_blocks = core_blocks.CuratedTopicBlock().child_blocks
    assert type(child_blocks['title']) is blocks.CharBlock
    assert type(child_blocks['pages']) is blocks.ListBlock
    assert type(child_blocks['pages'].child_block) is blocks.PageChooserBlock


def test_button_block():
    assert issubclass(core_blocks.ButtonBlock, blocks.StructBlock)
    child_blocks = core_blocks.ButtonBlock().child_blocks
    assert type(child_blocks['label']) is blocks.CharBlock
    assert type(child_blocks['link']) is core_blocks.LinkBlock


def test_video_block():
    assert issubclass(core_blocks.VideoBlock, blocks.StructBlock)
    child_blocks = core_blocks.VideoBlock().child_blocks
    assert type(child_blocks['width']) is blocks.IntegerBlock
    assert type(child_blocks['height']) is blocks.IntegerBlock
    assert type(child_blocks['video']) is core_blocks.MediaChooserBlock
