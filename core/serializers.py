from rest_framework import serializers


class CompanySerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False)
    expertise_industries = serializers.JSONField()
    expertise_countries = serializers.JSONField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
