import calendar
from functools import reduce

from directory_constants import choices
from . import helpers, serializers


class ExportPlanParser:
    """
        Parse the export plan details provided by directory-api's exportplan
        serializer
    par
    """

    PAYMENT_METHOD_OPTIONS = dict(choices.PAYMENT_METHOD_OPTIONS)
    PAYMENT_TERM_OPTIONS = dict(choices.PAYMENT_TERM_OPTIONS)
    ALL_TRANSPORT_OPTIONS = dict(choices.TRANSPORT_OPTIONS + choices.WATER_TRANSPORT_OPTIONS)
    EXPORT_UNITS = dict(choices.EXPORT_UNITS)
    MARKET_ROUTES = dict(choices.MARKET_ROUTE_CHOICES)
    PRODUCT_PROMOTIONS = dict(choices.PRODUCT_PROMOTIONAL_CHOICES)
    FUNDING_OPTIONS = dict(choices.FUNDING_OPTIONS)

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
            values=[self.get_key('getting_paid.incoterms.transport')],
            choices=self.ALL_TRANSPORT_OPTIONS,
        )
        self.set_key('getting_paid.incoterms.incoterms_transport_label', incoterms_transport_label)

        self.set_key(
            'getting_paid.payment_terms.terms_label',
            helpers.values_to_labels(
                values=[self.get_key('getting_paid.payment_terms.terms')],
                choices=self.PAYMENT_TERM_OPTIONS,
            ),
        )

        unit_value = self.get_key('total_cost_and_price.export_quantity.value')
        unit_label = helpers.values_to_labels(
            values=[self.get_key('total_cost_and_price.export_quantity.unit')] or [],
            choices=self.EXPORT_UNITS,
        )

        export_quantity_label = f'{unit_value} {unit_label}' if unit_value and unit_label else ''
        self.set_key('total_cost_and_price.export_quantity_label', export_quantity_label)

        export_end_month = self.get_key('total_cost_and_price.export_end.month')
        export_end_year = self.get_key('total_cost_and_price.export_end.year')

        export_end_label = (
            f'{calendar.month_name[export_end_month]} {export_end_year}'
            if (export_end_month and export_end_year)
            else ''
        )
        self.set_key('total_cost_and_price.export_end_label', export_end_label)

        for route in self.data.get('route_to_markets', []):
            route_label = helpers.values_to_labels(values=[route.get('route')] or [], choices=self.MARKET_ROUTES)
            promote_label = helpers.values_to_labels(values=[route.get('promote')], choices=self.PRODUCT_PROMOTIONS)
            if route_label:
                route['route_label'] = route_label
            if promote_label:
                route['promote_label'] = promote_label

        for funding in self.data.get('funding_credit_options', []):
            funding_label = helpers.values_to_labels(
                values=[funding.get('funding_option')], choices=self.FUNDING_OPTIONS
            )
            if funding_label:
                funding['funding_option_label'] = funding_label

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
