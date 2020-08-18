from unittest import mock

import pytest
from wagtail.core import blocks

from core import blocks as core_blocks
from tests.unit.core.factories import ContentModuleFactory, DetailPageFactory


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


@pytest.mark.django_db
def test_modular_content_static_block_render():
    module = ContentModuleFactory()
    module.tags.add('tag1', 'tag2')
    module.save()

    request = mock.Mock(GET={'tags': 'tag1,tag2'})
    block = core_blocks.ModularContentStaticBlock()
    context = {'request': request}
    html = block.render(context=context, value=module.content)
    expected_html = '\n<div class="modules">\n\n     <p class="m-b-0 "><div class="rich-text">{}</div></p>\n\n</div>\n'.format(module.content)  # noqa
    assert html == expected_html


def test_render_form_with_constructor():
    block = core_blocks.ModularContentStaticBlock()
    rendered_html = block.render_form(None)
    assert rendered_html == 'Content modules will be automatically displayed, no configuration needed.'


def test_basic_render_form_for_media_chooser_block():
    block = core_blocks.MediaChooserBlock()
    with pytest.raises(NotImplementedError):
        block.render_basic(value=None)


@pytest.mark.django_db
def test_internal_link_structure_value(domestic_homepage):
    page = DetailPageFactory(parent=domestic_homepage)
    block = core_blocks.LinkBlock()
    value = block.to_python({
        'internal_link': page.id,
    })
    assert page.url_path == value.url


@pytest.mark.django_db
def test_external_link_structure_value(domestic_homepage):
    block = core_blocks.LinkBlock()
    value = block.to_python({
        'external_link': 'http://great.gov.uk'
    })
    assert value.url == 'http://great.gov.uk'


@pytest.mark.django_db
def test_learning_link_component(domestic_homepage):
    test_title = 'Detail page title'
    override_title = 'Overidden title'
    override_lede = 'Overidden lede'
    target_page = DetailPageFactory(parent=domestic_homepage, title=test_title)
    link_block = core_blocks.SidebarLinkBlock()
    # Render values from linked page
    result = link_block.render(value={'link': {'internal_link': target_page}}, context={})
    assert test_title in result
    assert domestic_homepage.title in result
    # Override the title and lede
    result_override = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': target_page}
        },
        context={})
    assert override_title in result_override
    assert domestic_homepage.title in result_override
