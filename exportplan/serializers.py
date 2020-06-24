from rest_framework import serializers


class ExportPlanRecommendedCountriesSerializer(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.CharField())

    def validate_sectors(self, value):
        if value:
            return value[0].split(',')
        else:
            raise serializers.ValidationError('sectors is a required field')


class BrandAndProductDetailsSerializer(serializers.Serializer):
    story = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    processes = serializers.CharField(required=False, allow_blank=True)
    packaging = serializers.CharField(required=False, allow_blank=True)


class ExportPlanSerializer(serializers.Serializer):
    target_markets = serializers.ListField(child=serializers.CharField(), required=False)
    brand_product_details = BrandAndProductDetailsSerializer(required=False)
    rational = serializers.CharField(required=False, allow_blank=True)

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


class NewObjectiveSerializer(ObjectiveSerializer):
    pk = serializers.IntegerField(required=False)


class PkOnlySerializer(serializers.Serializer):
    pk = serializers.IntegerField()


class ExportPlanCountrySerializer(serializers.Serializer):
    country = serializers.CharField()
