from unittest import mock

from exportplan.context import InsightDataContextProvider, PDFContextProvider


def test_pdf_context_provider(get_request):

    pdf_context = PDFContextProvider().get_context_provider_data(get_request)

    assert len(pdf_context['export_plan']) == len(get_request.user.export_plan.data)
    assert pdf_context['user'] == get_request.user
    assert pdf_context['sections'] is not None
    assert pdf_context['calculated_pricing'] is not None
    assert pdf_context['host_url'] == ''


def test_insightdata_context_provider(mock_get_comtrade_data, multiple_country_data, get_request):
    context = InsightDataContextProvider().get_context_provider_data(get_request)

    assert mock_get_comtrade_data.call_count == 1
    assert mock_get_comtrade_data.call_args == mock.call(commodity_code='220850', countries_list=['NL'])
    assert context['insight_data'] == mock_get_comtrade_data.return_value
    assert context['insight_data']['NL']['country_data'] == multiple_country_data['NL']
