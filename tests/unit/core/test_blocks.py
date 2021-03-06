from unittest import mock

import pytest
from wagtail.core import blocks
from wagtail.core.blocks.stream_block import StreamBlockValidationError

from core import blocks as core_blocks
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
    expected_html = f'\n<div class="modules">\n\n     <p class="m-b-0 ">{module.content}</p>\n\n</div>\n'
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
    value = block.to_python({'internal_link': page.id})
    assert page.url_path == value.url


@pytest.mark.django_db
def test_external_link_structure_value(domestic_homepage):
    block = core_blocks.LinkBlock()
    value = block.to_python({'external_link': 'http://great.gov.uk'})
    assert value.url == 'http://great.gov.uk'


@pytest.mark.django_db
def test_learning_link_component(domestic_site, domestic_homepage):
    test_detail_title = 'Detail page title'
    test_list_title = 'List page title'
    override_title = 'Overidden title'
    override_lede = 'Overidden lede'
    test_external_link = 'external/link'
    target_detail_page = DetailPageFactory(
        parent=domestic_homepage, title=test_detail_title, estimated_read_duration='0:02:30'
    )
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
            'link': {'internal_link': target_detail_page, 'external_link': ''},
        },
        context={},
    )
    assert override_title in result_override
    assert override_lede in result_override
    assert test_detail_title not in result_override
    result_nolink = link_block.render(
        value={'title_override': override_title, 'lede_override': override_lede, 'link': None},
        context={},
    )
    assert override_title in result_nolink
    # Provide external link
    result_external_link = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': None, 'external_link': test_external_link},
        },
        context={},
    )
    assert test_external_link in result_external_link
    # Non detail page
    result_list_link = link_block.render(
        value={
            'title_override': override_title,
            'lede_override': override_lede,
            'link': {'internal_link': target_list_page, 'external_link': test_external_link},
        },
        context={},
    )
    assert 'Go' in result_list_link
    assert target_list_page.get_url() in result_list_link


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_no_personalisation_selection(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('123456', '1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('334455')
    case_study_2.country_code_tags.add('Europe', 'DE')
    case_study_2.save()

    # Empty personalisation selection
    mocked_export_plan = dict()

    request = rf.get('/', {})
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()
        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' not in context


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_only_country_selection(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('123456', '1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('334455')
    case_study_2.country_code_tags.add('Asia Pacific')
    case_study_2.save()

    # country personalisation selection
    mocked_export_plan = {
        'export_countries': [
            {
                'region': 'Asia Pacific',
                'country_name': 'Australia',
                'country_iso2_code': 'AU',
            }
        ]
    }

    request = rf.get('/', {})
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()
        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' in context
        assert context['case_study'] == case_study_2


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_only_product_selection(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('123456', '1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('334455')
    case_study_2.country_code_tags.add('Europe', 'HU')
    case_study_2.save()

    # product personalisation selection
    mocked_export_plan = {'export_commodity_codes': [{'commodity_code': '334455', 'commodity_name': 'Blah'}]}

    request = rf.get('/', {})
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()
        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' in context
        assert context['case_study'] == case_study_2


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_case_study_with_no_tags(rf, user):
    CaseStudyFactory()
    CaseStudyFactory()

    # personalised selection exist in export plan
    mocked_export_plan = {
        'export_commodity_codes': [{'commodity_code': '123456', 'commodity_name': 'Blah'}],
        'export_countries': [{'region': 'Europe', 'country_name': 'Hungary', 'country_iso2_code': 'HU'}],
    }

    request = rf.get('/', {})
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()
        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' not in context


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_case_study_with_tags_and_personalised_selection(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('123456', '1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('334455')
    case_study_2.country_code_tags.add('Europe', 'DE')
    case_study_2.save()

    mocked_export_plan = {
        'export_commodity_codes': [{'commodity_code': '123456', 'commodity_name': 'Something'}],
        'export_countries': [{'region': 'Europe', 'country_name': 'Hungary', 'country_iso2_code': 'HU'}],
    }

    request = rf.get('/')
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()

        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' in context
        assert 'case_study' in block.get_context(value=None, parent_context=context)
        assert context['case_study'] == case_study_1


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_latest_case_study_multiple_tags(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.hs_code_tags.add('123456', '1234')
    case_study_1.country_code_tags.add('Europe', 'ES')
    case_study_1.save()

    # Another case study with same tags as latest modified
    case_study_2 = CaseStudyFactory()
    case_study_2.hs_code_tags.add('123456', '1234')
    case_study_2.country_code_tags.add('Europe', 'ES')
    case_study_2.save()

    mocked_export_plan = {
        'export_commodity_codes': [{'commodity_code': '123456', 'commodity_name': 'Something'}],
        'export_countries': [{'region': 'Europe', 'country_name': 'Spain', 'country_iso2_code': 'ES'}],
    }

    request = rf.get('/')
    request.user = user
    request.user.export_plan = mock.MagicMock()
    with mock.patch.object(request.user, 'export_plan', mocked_export_plan):
        block = core_blocks.CaseStudyStaticBlock()
        context = {'request': request, 'export_plan': request.user.export_plan}
        context = block._annotate_with_case_study(context)
        assert 'case_study' in context
        assert context['case_study'] == case_study_2


@pytest.mark.django_db
def test_case_study_static_block_annotate_with_no_export_plan(rf, user):
    case_study_1 = CaseStudyFactory()
    case_study_1.save()

    # Another case study with same tags as latest modified
    case_study_2 = CaseStudyFactory()
    case_study_2.save()

    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request}
    context = block._annotate_with_case_study(context)
    assert 'case_study' not in context


@pytest.mark.django_db
def test_case_study_static_block_get_context():
    with mock.patch('core.blocks.CaseStudyStaticBlock._annotate_with_case_study') as mock_annotate_with_case_study:

        mocked_returned_context = mock.Mock('Annotated context')
        mock_annotate_with_case_study.return_value = mocked_returned_context

        block = core_blocks.CaseStudyStaticBlock()
        context = block.get_context(value='test')

        assert context == mocked_returned_context
        assert mock_annotate_with_case_study.call_count == 1


@pytest.mark.parametrize(
    'blocks_to_create,expected_exception_message',
    (
        (1, 'There must be between two and six statistics in this panel'),
        (2, None),
        (3, None),
        (4, None),
        (5, None),
        (6, None),
        (7, 'There must be between two and six statistics in this panel'),
    ),
)
def test_general_statistics_streamfield_validation(blocks_to_create, expected_exception_message):

    value = [mock.Mock() for x in range(blocks_to_create)]

    if expected_exception_message:
        with pytest.raises(StreamBlockValidationError) as ctx:
            core_blocks.general_statistics_streamfield_validation(value)
            assert ctx.message == expected_exception_message
    else:
        try:
            core_blocks.general_statistics_streamfield_validation(value)  #
        except Exception as e:
            assert False, f'Should not have got a {e}'
