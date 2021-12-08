from django.core.validators import RegexValidator
from rest_framework import serializers

phone_uk_regex = RegexValidator(
    regex=r'^(?:0|\+?44)(?:\d\s?){9,10}$', message='Phone number must be entered in UK format.'
)


class SSOBusinessUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    mobile_phone_number = serializers.CharField(validators=[phone_uk_regex], allow_blank=True, default='')


class SSOBusinessVerifyCodeSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    code = serializers.CharField()
