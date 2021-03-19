from exportplan.core.parsers import ExportPlanParser


def test_export_plan_parser(export_plan_data):

    ep_parser = ExportPlanParser(export_plan_data)
    assert ep_parser.data == export_plan_data
    assert ep_parser.export_country_name == export_plan_data['export_countries'][0]['country_name']
    assert ep_parser.export_commodity_code == export_plan_data['export_commodity_codes'][0]['commodity_code']
    assert ep_parser.country_iso2_code == export_plan_data['export_countries'][0]['country_iso2_code']


def test_serialize_for_template(export_plan_data):

    ep_parser = ExportPlanParser(export_plan_data)

    assert ep_parser.data['getting_paid']['payment_method']['payment_method_label'] == (
        'Credit or debit card payments, Merchant services'
    )
    assert ep_parser.data['getting_paid']['incoterms']['incoterms_transport_label'] == 'Ex Works (EXW)'
    assert ep_parser.data['total_cost_and_price']['first_period_period_label'] == '22.0 metre(s)'
    assert ep_parser.data['total_cost_and_price']['second_period_period_label'] == '5.0 day(s)'
    assert ep_parser.data['route_to_markets'][0]['route_label'] == 'Direct sales'
    assert ep_parser.data['route_to_markets'][0]['promote_label'] == 'Online marketing'


def test_serialize_for_template_empty(export_plan_data):
    export_plan_data['getting_paid']['payment_method'] = {}
    export_plan_data['getting_paid']['incoterms'] = {}
    export_plan_data['total_cost_and_price']['units_to_export_first_period']['value'] = ''
    export_plan_data['total_cost_and_price']['units_to_export_first_period']['unit'] = ''
    export_plan_data['total_cost_and_price'] = {}
    export_plan_data['route_to_markets'] = []

    ep_parser = ExportPlanParser(export_plan_data)

    assert ep_parser.data['getting_paid']['payment_method']['payment_method_label'] == ''
    assert ep_parser.data['getting_paid']['incoterms']['incoterms_transport_label'] == ''
    assert ep_parser.data['total_cost_and_price']['first_period_period_label'] == ''
    assert ep_parser.data['total_cost_and_price']['second_period_period_label'] == ''
    assert len(ep_parser.data['route_to_markets']) == 0
