import datetime
from unittest import mock

import pytest
from wagtail.core import blocks

from core import blocks as core_blocks
from core.models import CaseStudy
from tests.unit.core.factories import (
    CaseStudyFactory,
    ContentModuleFactory,
    DetailPageFactory,
    ListPageFactory,
)


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
    expected_html = '\n<div class="modules">\n\n     <p class="m-b-0 ">{}</p>\n\n</div>\n'.format(module.content)  # noqa
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
def test_learning_link_component(domestic_site, domestic_homepage):
    test_detail_title = 'Detail page title'
    test_list_title = 'List page title'
    override_title = 'Overidden title'
    override_lede = 'Overidden lede'
    test_external_link = 'external/link'
    target_detail_page = DetailPageFactory(
        parent=domestic_homepage, title=test_detail_title, estimated_read_duration='0:02:30')
    target_list_page = ListPageFactory(parent=domestic_homepage, title=test_list_title)

    link_block = core_blocks.SidebarLinkBlock()
    # Render values from linked page
    result = link_block.render(value={'link': {'internal_link': target_detail_page, 'external_link': ''}}, context={})
    assert test_detail_title in result
    assert domestic_homepage.title in result
    assert '3 min' in result
    assert target_detail_page.get_url() in result
    # Override the title and lede
    result_override = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': target_detail_page, 'external_link': ''}
        },
        context={})
    assert override_title in result_override
    assert override_lede in result_override
    assert test_detail_title not in result_override
    result_nolink = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': None
        },
        context={})
    assert override_title in result_nolink
    # Provide external link
    result_external_link = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': None, 'external_link': test_external_link}
        },
        context={})
    assert test_external_link in result_external_link
    # Non detail page
    result_list_link = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': target_list_page, 'external_link': test_external_link}
        },
        context={})
    assert 'Go' in result_list_link
    assert target_list_page.get_url() in result_list_link


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_case_study(rf):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('HS123456', 'HS1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('HS334455')
    case_study_2.country_code_tags.add('Europe', 'DE')
    case_study_2.save()

    # no relevant tags -> no case study
    request = rf.get('/', {})
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    'case_study' not in context

    # Show HS tag match
    request = rf.get('/', {'hs-tag': 'HS123456'})
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_1

    request = rf.get('/', {'hs-tag': 'HS334455'})
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_2

    # Show country tag match
    request = rf.get('/', {'country-tag': 'DE'})
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_2

    request = rf.get('/', {'country-tag': 'ES'})
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_1

    # Show most recently updated is given priority
    _new_modified_time_for_cs2 = case_study_1.modified + datetime.timedelta(seconds=30)
    CaseStudy.objects.filter(id=case_study_2.id).update(modified=_new_modified_time_for_cs2)
    case_study_2.refresh_from_db()
    assert case_study_2.modified > case_study_1.modified

    request = rf.get('/', {'country-tag': 'Europe'})  # Will find multiple case studies
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_2

    _new_modified_time_for_cs1 = case_study_2.modified + datetime.timedelta(seconds=30)
    CaseStudy.objects.filter(id=case_study_1.id).update(modified=_new_modified_time_for_cs1)
    case_study_1.refresh_from_db()
    assert case_study_1.modified > case_study_2.modified

    # re-run the same call now the case study timestamps have changed
    context = block._annotate_with_case_study(context)
    assert context['case_study'] == case_study_1


@pytest.mark.django_db
def test_case_study_static_block_get_context():
    with mock.patch(
        'core.blocks.CaseStudyStaticBlock._annotate_with_case_study'
    ) as mock_annotate_with_case_study:

        mocked_returned_context = mock.Mock('Annotated context')
        mock_annotate_with_case_study.return_value = mocked_returned_context

        block = core_blocks.CaseStudyStaticBlock()
        context = block.get_context(value='test')

        assert context == mocked_returned_context
        assert mock_annotate_with_case_study.call_count == 1
