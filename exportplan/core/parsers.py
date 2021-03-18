from functools import reduce

from directory_constants import choices
from . import helpers, serializers


class ExportPlanParser:
    """
    Parse the export plan details provided by directory-api's exportplan
    serializer

    """

    PAYMENT_METHOD_OPTIONS = dict(choices.PAYMENT_METHOD_OPTIONS)
    ALL_TRANSPORT_OPTIONS = dict(choices.TRANSPORT_OPTIONS + choices.WATER_TRANSPORT_OPTIONS)
    EXPORT_UNITS = dict(choices.EXPORT_UNITS)
    EXPORT_TIMEFRAME = dict(choices.EXPORT_TIMEFRAME)
    MARKET_ROUTES = dict(choices.MARKET_ROUTE_CHOICES)
    PRODUCT_PROMOTIONS = dict(choices.PRODUCT_PROMOTIONAL_CHOICES)

    def __init__(self, data):
        self.data = data
        self.seralizer = serializers.ExportPlanSerializer(data=self.data)
        self.seralizer.is_valid()
        self.serialize_for_template()

    def __bool__(self):
        return bool(self.data)

    def get_key(self, key):
        try:
            return reduce(dict.get, key.split('.'), self.data)
        except TypeError:
            return None

    def set_key(self, key, value):
        set_value = value or ''
        key = key.split('.')
        try:
            my_dict = reduce(dict.get, key[:-1], self.data)
            my_dict[key[-1]] = set_value
        except TypeError:
            return None

    def serialize_for_template(self):
        payment_method_label = helpers.values_to_labels(
            values=self.get_key('getting_paid.payment_method.methods') or [],
            choices=self.PAYMENT_METHOD_OPTIONS,
        )
        self.set_key('getting_paid.payment_method.payment_method_label', payment_method_label)

        incoterms_transport_label = helpers.values_to_labels(
            values=[self.get_key('getting_paid.incoterms.transport')] or [],
            choices=self.ALL_TRANSPORT_OPTIONS,
        )
        self.set_key('getting_paid.incoterms.incoterms_transport_label', incoterms_transport_label)

        unit_value = self.get_key('total_cost_and_price.units_to_export_first_period.value')
        unit_label = helpers.values_to_labels(
            values=self.get_key('total_cost_and_price.units_to_export_first_period.unit') or [],
            choices=self.EXPORT_UNITS,
        )

        first_period_period_label = f'{unit_value} {unit_label}' if unit_value and unit_label else ''
        self.set_key('total_cost_and_price.first_period_period_label', first_period_period_label)

        unit_period_value = self.get_key('total_cost_and_price.units_to_export_second_period.value')

        unit_period_label = helpers.values_to_labels(
            values=self.get_key('total_cost_and_price.units_to_export_second_period.unit') or [],
            choices=self.EXPORT_TIMEFRAME,
        )
        second_period_period_label = (
            f'{unit_period_value} {unit_period_label}' if (unit_period_value and unit_period_value) else ''
        )
        self.set_key('total_cost_and_price.second_period_period_label', second_period_period_label)

        for route in self.data.get('route_to_markets', []):
            route_label = helpers.values_to_labels(values=[route.get('route')] or [], choices=self.MARKET_ROUTES)
            promote_label = helpers.values_to_labels(
                values=[route.get('promote')] or [], choices=self.PRODUCT_PROMOTIONS
            )
            if route_label:
                route['route_label'] = route_label
            if promote_label:
                route['promote_label'] = promote_label

    @property
    def export_country_name(self):
        if self.data.get('export_countries'):
            return self.data['export_countries'][0]['country_name']

    @property
    def country_iso2_code(self):
        if self.data.get('export_countries'):
            return self.data['export_countries'][0]['country_iso2_code']

    @property
    def export_country_code(self):
        if self.data.get('export_countries'):
            return self.data['export_countries'][0]['country_iso2_code']

    @property
    def export_commodity_code(self):
        if self.data.get('export_commodity_codes'):
            return self.data['export_commodity_codes'][0]['commodity_code']
