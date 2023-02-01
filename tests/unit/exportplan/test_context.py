from unittest import mock

from django.conf import settings

from exportplan.context import (
    CountryDataContextProvider,
    FactbookDataContextProvider,
    PDFContextProvider,
)


def test_pdf_context_provider(get_request, export_plan_data):
    pdf_context = PDFContextProvider().get_context_provider_data(get_request, id=1)

    assert pdf_context['export_plan'].data == export_plan_data
    assert pdf_context['user'] == get_request.user
    assert pdf_context['sections'] is not None
    assert pdf_context['calculated_pricing'] is not None
    assert pdf_context['contact_detail'] == {'email': 'great.support@trade.gov.uk'}
    assert pdf_context['pdf_statics_url'] == 'http://testserver/static/'


def test_pdf_context_pdf_statics_url_s3(get_request):
    settings.PDF_STATIC_URL = 'http://my_bucket.aws.my.region/pdf/'
    pdf_context = PDFContextProvider().get_context_provider_data(get_request, id=1)
    assert pdf_context['pdf_statics_url'] == 'http://my_bucket.aws.my.region/pdf/'


def test_country_data_context_provider(
    mock_get_comtrade_data, mock_api_get_country_data_by_country, multiple_country_data, get_request
):
    context = CountryDataContextProvider().get_context_provider_data(get_request, id=1)

    assert mock_get_comtrade_data.call_count == 1
    assert mock_get_comtrade_data.call_args == mock.call(commodity_code='220850', countries_list=['NL'])
    assert context['comtrade_data'] == mock_get_comtrade_data.return_value

    assert context['country_data']['urban_rural_percentages'] == {
        'urban_percentage': 0.3333,
        'rural_percentage': 0.6667,
        'total_population': 300,
    }
    assert context['country_data']['population_age_data']['marketing-approach'] == {
        'female_target_age_population': 6000,
        'male_target_age_population': 6000,
        'target_ages': ['0-14', '60+'],
        'total_target_age_population': 12000,
    }
    assert context['country_data']['total_population'] == 20000

    for fieldname in [
        'GDPPerCapita',
        'ConsumerPriceIndex',
        'Income',
        'CorruptionPerceptionsIndex',
        'EaseOfDoingBusiness',
        'InternetUsage',
        'PopulationUrbanRural',
        'PopulationData',
    ]:
        assert context['country_data'].get(fieldname) == multiple_country_data['NL'].get(fieldname)


def test_factbook_context_provider(mock_cia_world_factbook_data, get_request):
    context = FactbookDataContextProvider().get_context_provider_data(get_request, id=1)

    assert mock_cia_world_factbook_data.call_count == 1
    assert mock_cia_world_factbook_data.call_args == mock.call(country='Netherlands', key='people,languages')
    assert context['language_data'] == mock_cia_world_factbook_data.return_value
