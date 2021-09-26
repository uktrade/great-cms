from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from wagtail.core import blocks
from wagtail.core.blocks.stream_block import StreamBlockValidationError

from core import blocks as core_blocks
from core.models import CaseStudyScoringSettings
from core.utils import get_cs_ranking
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
def test_case_study_static_block(
    rf, user, client, magna_site, mock_get_user_data, mock_cs_update, mock_elasticsearch_count, mock_elasticsearch_scan
):
    case_study_1 = CaseStudyFactory(id=1)
    case_study_1.hs_code_tags.add('111111', '1234')
    case_study_1.country_code_tags.add('Germany')
    case_study_1.save()

    case_study_2 = CaseStudyFactory(id=2)
    case_study_2.hs_code_tags.add('334455')
    case_study_2.country_code_tags.add('Spain')
    case_study_2.save()

    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request, 'user': user}
    context = block._annotate_with_case_study(context)
    assert 'case_study' in context


@pytest.mark.django_db
def test_case_study_update_index(mock_elasticsearch_connect, mock_elasticsearch_get_connection):
    CaseStudyFactory(id=1)


base_settings = {
    'threshold': 12,
    'module': 2,
    'topic': 4,
    'lesson': 8,
    'product_hs6': 8,
    'product_hs4': 4,
    'product_hs2': 2,
    'country_region': 2,
    'country_exact': 4,
    'other_product_hs6': -0.5,
    'other_product_hs4': -0.25,
    'other_product_hs2': -0.125,
    'other_country_region': -0.125,
    'other_country_exact': -0.25,
    'recency_3_months': 8,
    'recency_6_months': 4,
    'recency_9_months': 2,
    'recency_12_months': 1,
    'recency_15_months': 0.5,
    'recency_18_months': 0.25,
    'recency_21_months': 0.125,
    'recency_24_months': 0,
    'trading_blocs': 2,
    'other_module_tags': -0.5,
    'other_topic_tags': -0.25,
    'other_lesson_tags': -0.1,
}


def get_case_study(data):
    base_cs = {
        'pk': '38',
        'hscodes': '',
        'lesson': '',
        'country': '',
        'region': '',
        'modified': (datetime.now(timezone.utc) - timedelta(days=31 * 30)).isoformat(),
    }
    base_cs.update(data or {})
    return base_cs


@pytest.mark.parametrize(
    'cs_tags, user_products, expected_score',
    (
        ('12', ['123456'], 2),
        ('12 1234', ['123456'], 4),
        ('123456', ['123456'], 8),
        ('12 6543', ['12345', '654321'], 4),
        ('12 654321', ['12345', '654321'], 8),
        ('12 654321', ['666666'], -0.5),
        ('12 6543', ['666666'], -0.25),
        ('12', ['666666'], -0.125),
    ),
)
def test_case_study_ranking_product(cs_tags, user_products, expected_score):
    cs = get_case_study({'hscodes': cs_tags})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, export_commodity_codes=user_products, settings=settings) == expected_score


@pytest.mark.parametrize(
    'cs_tags_markets, user_markets, expected_score',
    (
        ('Japan France', ['Japan', 'France'], 4),
        ('Spain France', ['Japan', 'France'], 4),
        ('Spain USA', ['Japan', 'France'], -0.25),
        ('', ['Japan', 'France'], 0),
    ),
)
def test_case_study_ranking_market(cs_tags_markets, user_markets, expected_score):
    cs = get_case_study({'country': cs_tags_markets})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, export_markets=user_markets, settings=settings) == expected_score


@pytest.mark.parametrize(
    'cs_tags_regions, user_regions, expected_score',
    (
        ('Asia_Pacific', ['North America', 'Asia Pacific'], 2),
        ('North_America', ['North America', 'Asia Pacific'], 2),
        ('South_America', ['North America', 'Asia Pacific'], -0.125),
        ('', ['North America', 'Asia Pacific'], 0),
        ('', [], 0),
    ),
)
def test_case_study_ranking_region(cs_tags_regions, user_regions, expected_score):
    cs = get_case_study({'region': cs_tags_regions})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, export_regions=user_regions, settings=settings) == expected_score


@pytest.mark.parametrize(
    'cs_tags_trading_blocks, user_trading_blocs, expected_score',
    (
        ('European_Union_(EU)', ['European Union (EU)', 'Economic Community of Central African States (ECCAS)'], 2),
        (
            'European_Economic_Area_(EEA)',
            ['European Union (EU)', 'Economic Community of Central African States (ECCAS)'],
            0,
        ),
        ('', ['European Union (EU)', 'Economic Community of Central African States (ECCAS)'], 0),
        ('', [], 0),
    ),
)
def test_case_study_ranking_trading_bloc(cs_tags_trading_blocks, user_trading_blocs, expected_score):
    cs = get_case_study({'tradingblocs': cs_tags_trading_blocks})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs=cs, export_blocs=user_trading_blocs, settings=settings) == expected_score


@pytest.mark.parametrize(
    'cs_tags_lesson, user_page_context, expected_score',
    (
        ('lesson_3', ['lesson_3', 'module_2', 'topic_1'], 8),
        ('module_2 topic_1 lesson_3', ['lesson_3', 'module_2', 'topic_1'], 14),
        ('module_2 topic_1', ['lesson_3', 'module_2', 'topic_1'], 6),
        ('module_2 topic_1 lesson_8', ['lesson_3', 'module_2', 'topic_1'], 5.9),
        ('module_2 topic_16 lesson_8', ['lesson_3', 'module_2', 'topic_1'], 1.65),
        ('module_9 topic_16 lesson_8', ['lesson_3', 'module_2', 'topic_1'], -0.85),
        ('', ['lesson_3', 'module_2', 'topic_1'], 0),
    ),
)
def test_case_study_ranking_lesson(cs_tags_lesson, user_page_context, expected_score):
    cs = get_case_study({'lesson': cs_tags_lesson})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, page_context=user_page_context, settings=settings) == expected_score


@pytest.mark.parametrize(
    'cs_age_days, expected_score',
    (
        (0, 8),
        (3 * 31, 4),
        (6 * 31, 2),
        (9 * 31, 1),
        (366, 0.5),
        (366 + (3 * 31), 0.25),
        (366 + (6 * 31), 0.125),
        (366 + (9 * 31), 0.0625),
        (366 * 2, 0.0625),
    ),
)
def test_case_study_ranking_recency(cs_age_days, expected_score):
    cs = get_case_study({'modified': (datetime.now(timezone.utc) - timedelta(days=cs_age_days)).isoformat()})
    base_settings.update({'recency_24_months': 0.0625})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, settings=settings) == expected_score


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


def test_video_chooser_block__render_basic():

    vcblock = core_blocks.VideoChooserBlock()

    assert vcblock.render_basic(None) == ''
    assert vcblock.render_basic('') == ''

    mock_value = mock.Mock(name='mock VideoChooserBlock value')

    mock_value.file.url = 'mocked url attr'

    assert vcblock.render_basic(mock_value) == 'mocked url attr'
