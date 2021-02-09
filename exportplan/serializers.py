import datetime
import decimal
import json

from directory_validators.string import no_html
from rest_framework import serializers

from exportplan.utils import format_two_dp


class ExportPlanRecommendedCountriesSerializer(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.CharField())

    def validate_sectors(self, value):
        return value[0].split(',')


class CountryTargetAgeDataSerializer(serializers.Serializer):
    target_age_groups = serializers.ListField(child=serializers.CharField())
    country = serializers.CharField()
    section_name = serializers.CharField()

    def validate_target_age_groups(self, value):
        return value[0].split(',')


class AboutYourBuinessSerializer(serializers.Serializer):
    story = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    location = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    processes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    packaging = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    performance = serializers.CharField(required=False, allow_blank=True, validators=[no_html])


class ObjectiveSerializer(serializers.Serializer):
    rationale = serializers.CharField(required=False, allow_blank=True, validators=[no_html])


class TargetMarketsResearchSerializer(serializers.Serializer):
    demand = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    competitors = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    trend = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    unqiue_selling_proposition = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    average_price = serializers.IntegerField(
        required=False,
        allow_null=True,
    )


class MarketingApproachSerializer(serializers.Serializer):
    resources = serializers.CharField(required=False, allow_blank=True, validators=[no_html])


class AdaptationTargetMarketSerializer(serializers.Serializer):
    labelling = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    packaging = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    size = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    standards = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    translations = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    other_changes = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    certificate_of_origin = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    insurance_certificate = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    commercial_invoice = serializers.CharField(required=False, allow_null=True, validators=[no_html])
    uk_customs_declaration = serializers.CharField(required=False, allow_null=True, validators=[no_html])


class ExportPlanCountrySerializer(serializers.Serializer):
    country_name = serializers.CharField(required=True)
    country_iso2_code = serializers.CharField(required=False, allow_null=True)
    region = serializers.CharField(required=False, allow_null=True)


class ExportPlanCommodityCodeSerializer(serializers.Serializer):
    commodity_name = serializers.CharField(required=True)
    commodity_code = serializers.CharField(required=True)


class UiOptions(serializers.Serializer):
    target_ages = serializers.ListField(child=serializers.CharField())

    def validate_target_ages(self, value):
        return value[0].split(',')


class UiProgress(serializers.Serializer):
    is_complete = serializers.BooleanField(required=False)
    date_last_visited = serializers.CharField(required=False)
    modified = serializers.DateTimeField(required=False)

    def to_representation(self, instance):
        modified = instance.get('modified')
        if isinstance(modified, (datetime.date, datetime.datetime)):
            instance['date_last_visited'] = modified.isoformat()
            instance.pop('modified')
        return instance

    class Meta:
        exclude = ('ts',)


class FundingAndCreditSerializer(serializers.Serializer):
    override_estimated_total_cost = serializers.FloatField(required=False)
    funding_amount_required = serializers.FloatField(required=False)


class DirectCostsSerializer(serializers.Serializer):
    product_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    labour_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    other_direct_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    @property
    def total_direct_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.get_fields().keys():
            total = total + float(self.data.get(field, 0.00))
        return total


class OverheadCostsSerializer(serializers.Serializer):
    product_adaption = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    freight_logistics = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    agent_distributor_fees = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    marketing = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    insurance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    other_overhead_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    @property
    def total_overhead_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.get_fields().keys():
            total = total + float(self.data.get(field, 0.00))
        return total


class TotalCostAndPriceSerializer(serializers.Serializer):
    class UnitRecordInt(serializers.Serializer):
        unit = serializers.CharField(required=False, default='', allow_blank=True)
        value = serializers.IntegerField(required=False)

        def to_internal_value(self, data):
            if data.get('value') == '':
                data['value'] = 0
            return super().to_internal_value(data)

    class UnitRecordDecimal(serializers.Serializer):
        unit = serializers.CharField(required=False, default='', allow_blank=True)
        value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0)

        def to_internal_value(self, data):
            if data.get('value') == '':
                data['value'] = 0.00
            return super().to_internal_value(data)

    units_to_export_first_period = UnitRecordInt(required=False)
    units_to_export_second_period = UnitRecordInt(required=False)
    final_cost_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    average_price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    net_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    local_tax_charges = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    duty_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    gross_price_per_unit_invoicing_currency = UnitRecordDecimal(required=False)

    @property
    def profit_per_unit(self):
        self.is_valid()
        profit_per_unit = 0.00
        if self.data.get('net_price') and self.data.get('final_cost_per_unit'):
            profit_per_unit = float(self.data['net_price']) - float(self.data['final_cost_per_unit'])
        return profit_per_unit

    @property
    def gross_price_per_unit(self):
        self.is_valid()
        duty_per_unit = self.data.get('duty_per_unit', 0.00)
        net_price = self.data.get('net_price', 0.00)
        local_tax_charges = self.data.get('local_tax_charges', 0.00)
        gross_price_per_unit = float(duty_per_unit) + float(local_tax_charges) + float(net_price)

        return gross_price_per_unit

    @property
    def potential_total_profit(self):
        self.is_valid()
        no_of_unit = self.data.get('units_to_export_first_period', {}).get('value')
        profit_per_unit = self.profit_per_unit
        potential_total_profit = 0.00
        if no_of_unit and profit_per_unit:
            potential_total_profit = profit_per_unit * float(no_of_unit)
        return potential_total_profit


class GettingPaidSerializer(serializers.Serializer):
    class PaymentMethodSerializer(serializers.Serializer):
        methods = serializers.ListField(child=serializers.CharField(), required=False)
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    class PaymentTermsSerializer(serializers.Serializer):
        terms = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    class IncotermsSerializer(serializers.Serializer):
        transport = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    payment_method = PaymentMethodSerializer(required=False)
    payment_terms = PaymentTermsSerializer(required=False)
    incoterms = IncotermsSerializer(required=False)


class ExportPlanSerializer(serializers.Serializer):
    export_commodity_codes = ExportPlanCommodityCodeSerializer(many=True, required=False)
    export_countries = ExportPlanCountrySerializer(many=True, required=False)
    target_markets = serializers.ListField(child=serializers.CharField(), required=False)
    about_your_business = AboutYourBuinessSerializer(required=False)
    objectives = ObjectiveSerializer(required=False)
    target_markets_research = TargetMarketsResearchSerializer(required=False)
    marketing_approach = MarketingApproachSerializer(required=False)
    adaptation_target_market = AdaptationTargetMarketSerializer(required=False)
    ui_options = UiOptions(required=False)
    ui_progress = serializers.DictField(child=UiProgress(), required=False)
    direct_costs = DirectCostsSerializer(required=False)
    overhead_costs = OverheadCostsSerializer(required=False)
    total_cost_and_price = TotalCostAndPriceSerializer(required=False)
    funding_and_credit = FundingAndCreditSerializer(required=False)
    getting_paid = GettingPaidSerializer(required=False)

    def to_internal_value(self, data):
        internal_val = super().to_internal_value(data)
        if internal_val.get('ui_progress') == {}:
            internal_val.pop('ui_progress')
        return internal_val

    @property
    def total_direct_costs(self):
        self.is_valid()
        total_direct_costs = 0.00
        if self.data.get('direct_costs'):
            total_direct_costs = DirectCostsSerializer(data=self.data['direct_costs']).total_direct_costs
        return total_direct_costs

    @property
    def total_overhead_costs(self):
        self.is_valid()
        total_overhead_costs = 0.00
        if self.data.get('overhead_costs'):
            total_overhead_costs = OverheadCostsSerializer(data=self.data['overhead_costs']).total_overhead_costs
        return total_overhead_costs

    @property
    def total_export_costs(self):
        self.is_valid()
        units_to_export = self.data.get('total_cost_and_price', {}).get('units_to_export_first_period', {}).get('value')
        total_export_costs = 0.00
        if units_to_export:
            total_export_costs = (self.total_direct_costs * float(units_to_export)) + self.total_overhead_costs
        return total_export_costs

    @property
    def estimated_costs_per_unit(self):
        self.is_valid()
        units_to_export = float(
            self.data.get('total_cost_and_price', {}).get('units_to_export_first_period', {}).get('value', 0.00)
        )
        estimated_costs_per_unit = float(self.total_direct_costs)
        if self.total_overhead_costs > 0.00 and units_to_export > 0.00:
            estimated_costs_per_unit = (self.total_overhead_costs / float(units_to_export)) + float(
                self.total_direct_costs
            )
        return estimated_costs_per_unit

    @property
    def calculate_cost_pricing(self):
        self.is_valid()
        calculated_dict = {
            'total_direct_costs': format_two_dp(self.total_direct_costs),
            'total_overhead_costs': format_two_dp(self.total_overhead_costs),
        }

        serializer = TotalCostAndPriceSerializer(data=self.data.get('total_cost_and_price'))
        calculated_dict.update(
            {
                'profit_per_unit': format_two_dp(serializer.profit_per_unit),
                'potential_total_profit': format_two_dp(serializer.potential_total_profit),
                'gross_price_per_unit': format_two_dp(serializer.gross_price_per_unit),
            }
        )
        calculated_dict['total_export_costs'] = format_two_dp(self.total_export_costs)
        calculated_dict['estimated_costs_per_unit'] = format_two_dp(self.estimated_costs_per_unit)
        return calculated_dict

    def cost_and_pricing_to_json(self, data):
        # This method currently takes in cost and pricing data and serialising to JSON format
        # Required for UI since it requires defaults
        # This is horrible and will need to be reworked
        # TODO move this to a export plan parser helper method
        direct_cost_json = self.serialise_to_json(DirectCostsSerializer(data=data.get('direct_costs', {})))
        overhead_costs_json = self.serialise_to_json(OverheadCostsSerializer(data=data.get('overhead_costs', {})))
        total_cost_and_price_json = self.serialise_to_json(
            TotalCostAndPriceSerializer(data=data.get('total_cost_and_price', {}))
        )

        cost_pricing_data = {
            'direct_costs': direct_cost_json,
            'overhead_costs': overhead_costs_json,
            'total_cost_and_price': total_cost_and_price_json,
        }
        json_encoded = json.dumps(cost_pricing_data, cls=self.DecimalEncoder)
        return json_encoded

    def serialise_to_json(self, serialiser):
        serialiser.is_valid()
        to_json = {}
        for k, v in serialiser.fields.items():
            val = self.get_default_value(v)
            to_json.update({k: serialiser.validated_data.get(k, val)})
        return to_json

    def get_default_value(self, field_type):
        if isinstance(field_type, serializers.DecimalField):
            return ''
        elif isinstance(field_type, TotalCostAndPriceSerializer.UnitRecordInt) or isinstance(
            field_type, TotalCostAndPriceSerializer.UnitRecordDecimal
        ):
            return {'unit': '', 'value': ''}

    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)


class CompanyObjectiveSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    planned_reviews = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    owner = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[no_html])
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()

    # convert empty strings to null values
    def validate_start_date(self, value):
        if value == '':
            return None
        return value

    def validate_end_date(self, value):
        if value == '':
            return None
        return value


class RouteToMarketSerializer(serializers.Serializer):
    route = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    promote = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    market_promotional_channel = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class TargetMarketDocumentSerializer(serializers.Serializer):
    document_name = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    note = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class FundingCreditOptionsSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False)
    funding_option = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class BusinessTripsSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class NewFundingCreditOptionsSerializer(FundingCreditOptionsSerializer):
    pk = serializers.IntegerField(required=False)


class NewTargetMarketDocumentSerializer(TargetMarketDocumentSerializer):
    pk = serializers.IntegerField(required=False)


class NewRouteToMarketSerializer(RouteToMarketSerializer):
    pk = serializers.IntegerField(required=False)


class NewObjectiveSerializer(CompanyObjectiveSerializer):
    pk = serializers.IntegerField(required=False)


class PkOnlySerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class NewBusinessTripsSerializer(BusinessTripsSerializer):
    pk = serializers.IntegerField(required=False)
