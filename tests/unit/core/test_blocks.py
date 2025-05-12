from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from django.forms import Media
from opensearchpy.exceptions import ConnectionError, NotFoundError
from wagtail import blocks
from wagtail.blocks.stream_block import StreamBlockValidationError

from core import blocks as core_blocks, case_study_index
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
    expected_html = f'\n<div class="modules">\n    \n        <p class="m-b-0 ">{module.content}</p>\n    \n</div>\n'
    assert html == expected_html


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
def test_case_study_update_index(mock_opensearch_get_connection):
    # Check that the index is updated on create of a case study.
    CaseStudyFactory(id=1)


@mock.patch.object(case_study_index, 'delete_cs_index')
@pytest.mark.django_db
def test_case_study_delete_index(mock_delete_cs_index, mock_opensearch_get_connection):
    # Check that the index is deleted on delete of a case study.
    case_study_1 = CaseStudyFactory(id=1)
    case_study_1.delete()
    mock_delete_cs_index.assert_called()
    assert mock_delete_cs_index.call_args == mock.call(1)


@pytest.mark.django_db
def test_case_study_static_block_below_threshold(
    rf,
    user,
    client,
    magna_site,
    mock_get_user_data,
    mock_opensearch_get_connection,
    mock_opensearch_count,
    mock_opensearch_scan,
    mock_trading_blocs,
    settings,
):
    # Create a case-study that matches but below threshold score.  Check it's not shown.
    case_study_1 = CaseStudyFactory(id=1)
    case_study_1.hs_code_tags.add('334455')
    case_study_1.country_code_tags.add('Spain')
    case_study_1.save()

    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request, 'user': user}
    context = block._annotate_with_case_study(context)
    assert 'case_study' not in context


@pytest.mark.django_db
@pytest.mark.parametrize(
    'feature_show_list',
    (
        True,
        False,
    ),
)
def test_case_study_static_block_above_threshold(
    rf,
    user,
    client,
    magna_site,
    mock_get_user_data,
    mock_opensearch_get_connection,
    mock_opensearch_count,
    mock_opensearch_scan,
    mock_trading_blocs,
    settings,
    feature_show_list,
):
    # switch test cs listing on or off
    settings.FEATURE_SHOW_CASE_STUDY_RANKINGS = feature_show_list

    # Create two case studies - one above, and one below threshold.  check that the higher one is shown.
    case_study_1 = CaseStudyFactory(id=1)
    case_study_1.hs_code_tags.add('334455')
    case_study_1.country_code_tags.add('Spain')
    case_study_1.save()

    case_study_2 = CaseStudyFactory(id=2)
    case_study_2.hs_code_tags.add('111111', '1234')
    case_study_2.country_code_tags.add('Germany')
    case_study_2.save()

    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request, 'user': user}
    context = block._annotate_with_case_study(context)

    assert 'case_study' in context
    assert context.get('case_study').id == 2
    if feature_show_list:
        assert context['feature_show_case_study_list']
        assert context['case_study_list'][0]['score'] == 12
        assert context['case_study_list'][0]['pk'] == '2'
    else:
        assert 'feature_case_study_list' not in context


@pytest.mark.django_db
@mock.patch.object(core_blocks.CaseStudyStaticBlock, '_get_case_study_list')
def test_case_study_static_block_no_exception_raised_missing_casestudy(
    mock_get_case_study_list,
    rf,
    user,
    client,
    magna_site,
    mock_get_user_data,
    mock_opensearch_get_connection,
    mock_opensearch_count,
    mock_opensearch_scan,
    mock_trading_blocs,
    settings,
):
    # Create case studies - then delete it so there's a mismatch between ES and Database
    # Case study display shouldn't break
    case_study_1 = CaseStudyFactory(id=1)
    case_study_1.hs_code_tags.add('111111', '1234')
    case_study_1.country_code_tags.add('Germany')
    case_study_1.save()
    case_study_1.delete()
    mock_get_case_study_list.return_value = [{'pk': 1, 'score': 10000}]
    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request, 'user': user}
    context = block._annotate_with_case_study(context)

    assert 'case_study' not in context


@pytest.mark.django_db
@mock.patch.object(case_study_index, 'get_connection')
@pytest.mark.parametrize(
    'exception_type',
    (
        'connection',
        'index',
    ),
)
def test_connection_exception(
    mock_get_connection, rf, user, client, magna_site, mock_get_user_data, mock_trading_blocs, exception_type
):
    # Check that if no elastic search available, connection exceptions get caught.
    def raise_connection_error():
        if exception_type == 'connection':
            raise ConnectionError('Connection failed')
        else:
            raise NotFoundError('Not found')

    mock_get_connection.side_effect = raise_connection_error
    request = rf.get('/')
    request.user = user
    block = core_blocks.CaseStudyStaticBlock()
    context = {'request': request, 'user': user}
    context = block._annotate_with_case_study(context)
    assert 'case_study' not in context
    mock_get_connection.assert_called()


base_settings = {
    'threshold': 8,
    'module': 2,
    'topic': 4,
    'lesson': 8,
    'product_hs6': 8,
    'product_hs4': 4,
    'product_hs2': 2,
    'country_region': 2,
    'country_exact': 4,
    'trading_blocs': 2,
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
        ('12 654321', ['666666'], 0),
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
        ('Spain USA', ['Japan', 'France'], 0),
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
        ('module_2 topic_1 lesson_3', ['lesson_3', 'module_2', 'topic_1'], 8),
        ('module_2 topic_1', ['lesson_3', 'module_2', 'topic_1'], 4),
        ('module_2 topic_1 lesson_8', ['lesson_3', 'module_2', 'topic_1'], 4),
        ('module_2 topic_16 lesson_8', ['lesson_3', 'module_2', 'topic_1'], 2),
        ('', ['lesson_3', 'module_2', 'topic_1'], 0),
    ),
)
def test_case_study_ranking_lesson(cs_tags_lesson, user_page_context, expected_score):
    cs = get_case_study({'lesson': cs_tags_lesson})
    settings = CaseStudyScoringSettings(**base_settings)
    assert get_cs_ranking(cs, page_context=user_page_context, settings=settings) == expected_score


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


def test_individual_statistic_block_adaptor_media_property():
    individual_statistic_block_adaptor = core_blocks.IndividualStatisticBlockAdaptor()

    media = individual_statistic_block_adaptor.media

    # version may change
    expected = (
        '<script src="/static/wagtailadmin/js/telepath/blocks.js?v=260a4e4c"></script>\n'
        '<script src="/static/javascript/individualstatistic-block.js"></script>'
    )

    assert isinstance(media, Media) is True
    assert media.render() == expected
