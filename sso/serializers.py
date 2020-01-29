from rest_framework import serializers


class SSOBusinessUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
