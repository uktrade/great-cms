from directory_constants import choices
from . import helpers, serializers


class ExportPlanParser:
    """
    Parse the export plan details provided by directory-api's exportplan
    serializer

    """

    PAYMENT_METHOD_OPTIONS = dict(choices.PAYMENT_METHOD_OPTIONS)
    ALL_TRANSPORT_OPTIONS = dict(choices.TRANSPORT_OPTIONS + choices.WATER_TRANSPORT_OPTIONS)

    def __init__(self, data):
        self.data = data
        self.seralizer = serializers.ExportPlanSerializer(data=self.data)
        self.seralizer.is_valid()

    def __bool__(self):
        return bool(self.data)

    @property
    def export_country_name(self):
        if self.data.get('export_countries'):
            return self.data['export_countries'][0]['country_name']

    @property
    def export_country_code(self):
        if self.data.get('export_countries'):
            return self.data['export_countries'][0]['country_iso2_code']

    @property
    def export_commodity_code(self):
        if self.data.get('export_commodity_codes'):
            return self.data['export_commodity_codes'][0]['commodity_code']

    @property
    def getting_paid_payment_method_label(self):
        return helpers.values_to_labels(
            values=self.data.get('getting_paid', {}).get('payment_method', {}).get('methods') or [],
            choices=self.PAYMENT_METHOD_OPTIONS,
        )

    @property
    def getting_paid_incoterms_transport_label(self):
        return helpers.values_to_labels(
            values=[self.data.get('getting_paid', {}).get('incoterms', {}).get('transport')] or [],
            choices=self.ALL_TRANSPORT_OPTIONS,
        )
