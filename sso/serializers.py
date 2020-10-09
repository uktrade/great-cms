from rest_framework import serializers


class SSOBusinessUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class SSOBusinessVerifyCodeSerializer(serializers.Serializer):
    email = serializers.CharField()
    code = serializers.CharField()
