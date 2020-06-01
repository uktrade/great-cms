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

    def validate_target_markets(self, values):
        return [{'country': c} for c in values]


class ExportPlanCountrySerializer(serializers.Serializer):
    country = serializers.CharField()
