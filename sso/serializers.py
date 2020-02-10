from rest_framework import serializers


class SSOBusinessUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SSOBusinessVerifyCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    code = serializers.CharField()
