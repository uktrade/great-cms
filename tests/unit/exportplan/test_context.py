from unittest import mock

from exportplan.context import (
    FactbookDataContextProvider,
    InsightDataContextProvider,
    PDFContextProvider,
    PopulationAgeDataContextProvider,
)


def test_pdf_context_provider(get_request):

    pdf_context = PDFContextProvider().get_context_provider_data(get_request)

    assert len(pdf_context['export_plan'].data) == len(get_request.user.export_plan.data)
    assert pdf_context['user'] == get_request.user
    assert pdf_context['sections'] is not None
    assert pdf_context['calculated_pricing'] is not None
    assert pdf_context['contact_detail'] == {'email': 'great.support@trade.gov.uk'}
    assert pdf_context['host_url'] == 'testserver'


def test_insightdata_context_provider(mock_get_comtrade_data, multiple_country_data, get_request):
    context = InsightDataContextProvider().get_context_provider_data(get_request)

    assert mock_get_comtrade_data.call_count == 1
    assert mock_get_comtrade_data.call_args == mock.call(commodity_code='220850', countries_list=['NL'])
    assert context['insight_data'] == mock_get_comtrade_data.return_value
    assert context['insight_data']['NL']['country_data'] == multiple_country_data['NL']


def test_population_age_data_context_provider(mock_get_population_data, get_request):
    context = PopulationAgeDataContextProvider().get_context_provider_data(get_request)

    assert mock_get_population_data.call_count == 2
    assert mock_get_population_data.call_args_list[0] == mock.call(country='Netherlands', target_ages=['35-40'])
    assert mock_get_population_data.call_args_list[1] == mock.call(
        country='Netherlands', target_ages=['25-29', '47-49']
    )
    assert context['population_age_data']['marketing-approach'] == mock_get_population_data.return_value
    assert context['population_age_data']['target-markets-research'] == mock_get_population_data.return_value


def test_factbook_context_provider(mock_cia_world_factbook_data, get_request):
    context = FactbookDataContextProvider().get_context_provider_data(get_request)

    assert mock_cia_world_factbook_data.call_count == 1
    assert mock_cia_world_factbook_data.call_args == mock.call(country='Netherlands', key='people,languages')
    assert context['language_data'] == mock_cia_world_factbook_data.return_value
