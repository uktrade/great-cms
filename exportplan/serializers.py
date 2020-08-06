from rest_framework import serializers


class ExportPlanRecommendedCountriesSerializer(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.CharField())

    def validate_sectors(self, value):
        return value[0].split(',')


class PopulationDataSerializer(serializers.Serializer):
    target_age_groups = serializers.ListField(child=serializers.CharField())
    country = serializers.CharField()

    def validate_target_age_groups(self, value):
        return value[0].split(',')


class BrandAndProductDetailsSerializer(serializers.Serializer):
    story = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    processes = serializers.CharField(required=False, allow_blank=True)
    packaging = serializers.CharField(required=False, allow_blank=True)
    performance = serializers.CharField(required=False, allow_blank=True)


class TargetMarketsResearchSerializer(serializers.Serializer):
    demand = serializers.CharField(required=False, allow_blank=True)
    competitors = serializers.CharField(required=False, allow_blank=True)
    trend = serializers.CharField(required=False, allow_blank=True)
    unqiue_selling_proposition = serializers.CharField(required=False, allow_blank=True)
    average_price = serializers.IntegerField(required=False, allow_null=True)


class MarketingApproachSerializer(serializers.Serializer):
    resources = serializers.CharField(required=False, allow_blank=True)
    spending = serializers.IntegerField(required=False, allow_null=True)


class ExportPlanSerializer(serializers.Serializer):
    target_markets = serializers.ListField(child=serializers.CharField(), required=False)
    brand_product_details = BrandAndProductDetailsSerializer(required=False)
    rational = serializers.CharField(required=False, allow_blank=True)
    target_markets_research = TargetMarketsResearchSerializer(required=False)
    marketing_approach = MarketingApproachSerializer(required=False)

    def validate_target_markets(self, values):
        return [{'country': c} for c in values]


class ObjectiveSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True)
    planned_reviews = serializers.CharField(required=False, allow_blank=True)
    owner = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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
    route = serializers.CharField(required=False, allow_blank=True)
    promote = serializers.CharField(required=False, allow_blank=True)
    market_promotional_channel = serializers.CharField(required=False, allow_blank=True)
    companyexportplan = serializers.IntegerField()
    pk = serializers.IntegerField()


class NewRouteToMarketSerializer(RouteToMarketSerializer):
    pk = serializers.IntegerField(required=False)


class NewObjectiveSerializer(ObjectiveSerializer):
    pk = serializers.IntegerField(required=False)


class PkOnlySerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class ExportPlanCountrySerializer(serializers.Serializer):
    country = serializers.CharField()
