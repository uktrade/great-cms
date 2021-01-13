from directory_validators.string import no_html
from rest_framework import serializers


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


class DirectCostsSerializer(serializers.Serializer):
    product_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    labour_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    other_direct_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def calculate_total_direct_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.data:
            total = total + float(self.data[field])
        return total

class OverheadCostsSerializer(serializers.Serializer):
    product_adaption = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    freight_logistics = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    agent_distributor_fees = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    marketing = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    insurance = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    other_overhead_costs = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def calculate_total_overhead_costs(self):
        self.is_valid()
        total = 0.00
        for field in self.data:
            total = total + float(self.data[field])
        return total


class TotalCostAndPriceSerializer(serializers.Serializer):
    class UnitRecord(serializers.Serializer):
        unit = serializers.CharField(required=False)
        value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    units_to_export_first_period = UnitRecord(required=False)
    units_to_export_second_period = UnitRecord(required=False)
    final_cost_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    average_price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    net_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    local_tax_charges = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    duty_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    gross_price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    gross_price_per_unit_invoicing_currency = UnitRecord(required=False)
    profit_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    potential_total_profit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def calculate_profit_per_unit(self):
        self.is_valid()
        profit_per_unit = 0.00
        if self.data.get('net_price') and self.data.get('final_cost_per_unit'):
            profit_per_unit = float(self.data['net_price']) - float(self.data['final_cost_per_unit'])
        return profit_per_unit

    def calculate_potential_total_profit(self):
        self.is_valid()
        no_of_unit = self.data.get('units_to_export_first_period', {}).get('value')
        profit_per_unit = self.calculate_profit_per_unit()
        potential_total_profit = 0.00
        if no_of_unit and profit_per_unit:
            potential_total_profit = profit_per_unit * float(no_of_unit)
        return potential_total_profit

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
    direct_costs = DirectCostsSerializer(required=False)
    overhead_costs = OverheadCostsSerializer(required=False)
    total_cost_and_price = TotalCostAndPriceSerializer(required=False)

    def calculate_cost_pricing(self):
        self.is_valid()
        calculated_dict = {}
        if self.data.get('direct_costs'):
            calculated_dict.update(
                {
                    'total_direct_costs': DirectCostsSerializer(
                        data=self.data['direct_costs']).calculate_total_direct_costs()
                }
            )
        if self.data.get('overhead_costs'):
            calculated_dict.update(
                {
                    'total_overhead_costs': OverheadCostsSerializer(
                        data=self.data['overhead_costs']).calculate_total_overhead_costs()
                }
            )
        if self.data.get('total_cost_and_price'):
            serializer = TotalCostAndPriceSerializer(data=self.data['total_cost_and_price'])
            calculated_dict.update(
                {
                    'profit_per_unit': serializer.calculate_profit_per_unit(),
                    'potential_total_profit': serializer.calculate_potential_total_profit()
                }
            )
        return calculated_dict






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


class NewTargetMarketDocumentSerializer(TargetMarketDocumentSerializer):
    pk = serializers.IntegerField(required=False)


class NewRouteToMarketSerializer(RouteToMarketSerializer):
    pk = serializers.IntegerField(required=False)


class NewObjectiveSerializer(CompanyObjectiveSerializer):
    pk = serializers.IntegerField(required=False)


class PkOnlySerializer(serializers.Serializer):
    pk = serializers.IntegerField()
