from rest_framework import serializers
from directory_validators.string import no_html


class ExportPlanRecommendedCountriesSerializer(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.CharField())

    def validate_sectors(self, value):
        return value[0].split(',')


class PopulationDataSerializer(serializers.Serializer):
    country = serializers.CharField()


class CountryTargetAgeDataSerializer(serializers.Serializer):
    target_age_groups = serializers.ListField(child=serializers.CharField())
    country = serializers.CharField()

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
    average_price = serializers.IntegerField(required=False, allow_null=True,)


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


class ExportPlanSerializer(serializers.Serializer):
    export_commodity_codes = ExportPlanCommodityCodeSerializer(many=True, required=False)
    export_countries = ExportPlanCountrySerializer(many=True, required=False)
    target_markets = serializers.ListField(child=serializers.CharField(), required=False)
    about_your_business = AboutYourBuinessSerializer(required=False)
    objectives = ObjectiveSerializer(required=False)
    target_markets_research = TargetMarketsResearchSerializer(required=False)
    marketing_approach = MarketingApproachSerializer(required=False)
    adaptation_target_market = AdaptationTargetMarketSerializer(required=False)
    ui_option = UiOptions(required=False)

    def validate_target_markets(self, values):
        return [{'country': c} for c in values]


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
