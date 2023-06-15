from directory_validators.string import no_html
from django.core.validators import RegexValidator
from rest_framework import serializers

from regex import PHONE_NUMBER_REGEX_SIGNUP

phone_uk_regex = RegexValidator(regex=PHONE_NUMBER_REGEX_SIGNUP, message='Please enter a valid UK telephone number.')


class SSOBusinessUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    mobile_phone_number = serializers.CharField(validators=[phone_uk_regex], allow_blank=True, default='')


class SSOBusinessVerifyCodeSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    code = serializers.CharField()


class UserDataSerializer(serializers.Serializer):
    pass


class UserProductsSerializer(serializers.Serializer):
    commodity_name = serializers.CharField(validators=[no_html])
    commodity_code = serializers.CharField(validators=[no_html])


class QuestionnaireSerializer(serializers.Serializer):
    questionId = serializers.IntegerField()
    answer = serializers.CharField()
