from rest_framework import serializers


class CompaniesHouseSearchSerializer(serializers.Serializer):
    term = serializers.CharField()


class AddressSearchSerializer(serializers.Serializer):
    postcode = serializers.CharField()
