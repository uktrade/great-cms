from rest_framework import serializers


class SSOBusinessUserLoginForm(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
