from rest_framework import serializers


class ExportPlanRecommendedCountriesSerializer(serializers.Serializer):
    sectors = serializers.ListField(child=serializers.CharField())

    def validate_sectors(self, value):
        if value:
            return value[0].split(',')
        else:
            raise serializers.ValidationError('sectors is a required field')
