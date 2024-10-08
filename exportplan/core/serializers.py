import datetime
import decimal
import json

from directory_validators.string import no_html
from rest_framework import serializers

from directory_constants import choices
from exportplan.utils import format_two_dp


class CountryTargetAgeDataSerializer(serializers.Serializer):
    target_age_groups = serializers.ListField(
        required=False, allow_empty=True, allow_null=True, default=[], child=serializers.CharField()
    )
    section_name = serializers.CharField()


class CompanyObjectivesSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    planned_reviews = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    owner = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    end_month = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=12)
    end_year = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=9999)
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class AboutYourBuinessSerializer(serializers.Serializer):
    story = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    location = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    processes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    packaging = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    performance = serializers.ChoiceField(required=False, choices=choices.TURNOVER_CHOICES)


class ObjectiveSerializer(serializers.Serializer):
    rationale = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    company_objectives = serializers.ListField(child=CompanyObjectivesSerializer(), required=False)


class TargetMarketsResearchSerializer(serializers.Serializer):
    demand = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    competitors = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    trend = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    unqiue_selling_proposition = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    average_price = serializers.FloatField(required=False, allow_null=True)


class RouteToMarketsSerializer(serializers.Serializer):
    route = serializers.ChoiceField(required=False, allow_blank=True, choices=choices.MARKET_ROUTE_CHOICES)
    promote = serializers.ChoiceField(required=False, allow_blank=True, choices=choices.PRODUCT_PROMOTIONAL_CHOICES)
    market_promotional_channel = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class MarketingApproachSerializer(serializers.Serializer):
    resources = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    route_markets = serializers.ListField(child=RouteToMarketsSerializer(), required=False)


class TargetMarketDocumentsSerializer(serializers.Serializer):
    document_name = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    note = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class AdaptationTargetMarketSerializer(serializers.Serializer):
    labelling = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    packaging = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    size = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    standards = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    translations = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    other_changes = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    certificate_of_origin = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, validators=[no_html]
    )
    insurance_certificate = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, validators=[no_html]
    )
    commercial_invoice = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[no_html])
    uk_customs_declaration = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, validators=[no_html]
    )

    target_market_documents = serializers.ListField(child=TargetMarketDocumentsSerializer(), required=False)


class BusinessRisksSerializer(serializers.Serializer):
    risk = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[no_html])
    contingency_plan = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[no_html])
    risk_likelihood = serializers.ChoiceField(
        required=False, allow_blank=True, allow_null=True, choices=choices.RISK_LIKELIHOOD_OPTIONS
    )
    risk_impact = serializers.ChoiceField(
        required=False, allow_blank=True, allow_null=True, choices=choices.RISK_IMPACT_OPTIONS
    )
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


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


class FundingCreditOptionsSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False, allow_null=True)
    funding_option = serializers.ChoiceField(
        required=False, allow_null=True, allow_blank=True, choices=choices.FUNDING_OPTIONS
    )
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class FundingAndCreditSerializer(serializers.Serializer):
    override_estimated_total_cost = serializers.FloatField(required=False, allow_null=True)
    funding_amount_required = serializers.FloatField(required=False, allow_null=True)
    funding_credit_options = serializers.ListField(child=FundingCreditOptionsSerializer(), required=False)


class DirectCostsSerializer(serializers.Serializer):
    product_costs = serializers.FloatField(required=False, allow_null=True)
    labour_costs = serializers.FloatField(required=False, allow_null=True)
    other_direct_costs = serializers.FloatField(required=False, allow_null=True)

    @property
    def total_direct_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.get_fields().keys():
            total += float(self.data.get(field, 0.00) or 0.00)
        return total


class OverheadCostsSerializer(serializers.Serializer):
    product_adaption = serializers.FloatField(required=False, allow_null=True)
    freight_logistics = serializers.FloatField(required=False, allow_null=True)
    agent_distributor_fees = serializers.FloatField(required=False, allow_null=True)
    marketing = serializers.FloatField(required=False, allow_null=True)
    insurance = serializers.FloatField(required=False, allow_null=True)
    other_overhead_costs = serializers.FloatField(required=False, allow_null=True)

    @property
    def total_overhead_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.get_fields().keys():
            total += float(self.data.get(field, 0.00) or 0.00)
        return total


class TotalCostAndPriceSerializer(serializers.Serializer):
    class UnitRecordInt(serializers.Serializer):
        unit = serializers.CharField(required=False, default='', allow_blank=True)
        value = serializers.IntegerField(required=False, allow_null=True)

    class UnitRecordDecimal(serializers.Serializer):
        unit = serializers.CharField(required=False, default='', allow_blank=True)
        value = serializers.FloatField(required=False, allow_null=True)

    class MonthYearRecord(serializers.Serializer):
        month = serializers.IntegerField(required=False, allow_null=True)
        year = serializers.IntegerField(required=False, allow_null=True)

    export_quantity = UnitRecordInt(required=False)
    export_end = MonthYearRecord(required=False)
    final_cost_per_unit = serializers.FloatField(required=False, allow_null=True)
    average_price_per_unit = serializers.FloatField(required=False, allow_null=True)
    net_price = serializers.FloatField(required=False, allow_null=True)
    local_tax_charges = serializers.FloatField(required=False, allow_null=True)
    duty_per_unit = serializers.FloatField(required=False, allow_null=True)
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
        duty_per_unit = self.data.get('duty_per_unit', 0.00) or 0.00
        net_price = self.data.get('net_price', 0.00) or 0.00
        local_tax_charges = self.data.get('local_tax_charges', 0.00) or 0.00
        gross_price_per_unit = float(duty_per_unit) + float(local_tax_charges) + float(net_price)

        return gross_price_per_unit

    @property
    def potential_total_profit(self):
        self.is_valid()
        no_of_unit = self.data.get('export_quantity', {}).get('value') or 0
        profit_per_unit = self.profit_per_unit
        potential_total_profit = 0.00
        if no_of_unit and profit_per_unit:
            potential_total_profit = profit_per_unit * float(no_of_unit)
        return potential_total_profit


class ListMultipleChoiceField(serializers.MultipleChoiceField):
    def to_internal_value(self, data):
        return sorted(list(super().to_internal_value(data)))


class GettingPaidSerializer(serializers.Serializer):
    class PaymentMethodSerializer(serializers.Serializer):
        methods = ListMultipleChoiceField(required=False, allow_blank=True, choices=choices.PAYMENT_METHOD_OPTIONS)
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    class PaymentTermsSerializer(serializers.Serializer):
        terms = serializers.ChoiceField(required=False, allow_blank=True, choices=choices.PAYMENT_TERM_OPTIONS)
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    class IncotermsSerializer(serializers.Serializer):
        transport = serializers.ChoiceField(
            required=False, allow_blank=True, choices=choices.TRANSPORT_OPTIONS + choices.WATER_TRANSPORT_OPTIONS
        )
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    payment_method = PaymentMethodSerializer(required=False)
    payment_terms = PaymentTermsSerializer(required=False)
    incoterms = IncotermsSerializer(required=False)


class BusinessTripsSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class TravelBusinessPoliciesSerializer(serializers.Serializer):
    class VisaInformationSerializer(serializers.Serializer):
        visa_required = serializers.BooleanField(required=False, allow_null=True)
        how_where_visa = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
        how_long = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
        notes = serializers.CharField(required=False, allow_blank=True, validators=[no_html])

    travel_information = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    cultural_information = serializers.CharField(required=False, allow_blank=True, validators=[no_html])
    visa_information = VisaInformationSerializer(required=False)
    business_trips = serializers.ListField(child=BusinessTripsSerializer(), required=False)


class ExportPlanSerializer(serializers.Serializer):
    export_commodity_codes = ExportPlanCommodityCodeSerializer(many=True, required=False)
    export_countries = ExportPlanCountrySerializer(many=True, required=False)
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
    travel_business_policies = TravelBusinessPoliciesSerializer(required=False)
    business_risks = serializers.ListField(child=BusinessRisksSerializer(), required=False)

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
        export_quantity = self.data.get('total_cost_and_price', {}).get('export_quantity', {}).get('value') or 0
        total_export_costs = 0.00
        if export_quantity:
            total_export_costs = (self.total_direct_costs * float(export_quantity)) + self.total_overhead_costs
        return total_export_costs

    @property
    def estimated_costs_per_unit(self):
        self.is_valid()
        export_quantity = float(
            self.data.get('total_cost_and_price', {}).get('export_quantity', {}).get('value', 0.00) or 0
        )
        estimated_costs_per_unit = float(self.total_direct_costs or 0)
        if self.total_overhead_costs > 0.00 and export_quantity > 0.00:
            estimated_costs_per_unit = (self.total_overhead_costs / export_quantity) + float(
                self.total_direct_costs or 0
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
        elif isinstance(field_type, TotalCostAndPriceSerializer.MonthYearRecord):
            return {'month': '', 'year': ''}

    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)


class NewFundingCreditOptionsSerializer(FundingCreditOptionsSerializer):
    pk = serializers.IntegerField(required=False)


class NewTargetMarketDocumentsSerializer(TargetMarketDocumentsSerializer):
    pk = serializers.IntegerField(required=False)


class NewRouteToMarketsSerializer(RouteToMarketsSerializer):
    pk = serializers.IntegerField(required=False)


class NewCompanyObjectivesSerializer(CompanyObjectivesSerializer):
    pk = serializers.IntegerField(required=False)


class PkOnlySerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class NewBusinessTripsSerializer(BusinessTripsSerializer):
    pk = serializers.IntegerField(required=False)


class NewBusinessRisksSerializer(BusinessRisksSerializer):
    pk = serializers.IntegerField(required=False)
