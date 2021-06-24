from datetime import datetime

from django.utils.text import Truncator
from rest_framework import serializers


class ProductLookupSerializer(serializers.Serializer):
    tx_id = serializers.CharField(required=False)
    interaction_id = serializers.CharField(required=False)
    value_id = serializers.CharField(required=False)
    value_string = serializers.CharField(required=False)
    values = serializers.JSONField(required=False)
    proddesc = serializers.CharField(required=False)


class CompanySerializer(serializers.Serializer):
    MESSAGE_TOO_MANY_COUNTRIES = 'You can select a maximum of three countries.'

    expertise_industries = serializers.JSONField(required=False)
    expertise_countries = serializers.JSONField(required=False)
    expertise_products_services = serializers.JSONField(required=False)

    def validate_expertise_countries(self, value):
        if len(value) > 3:
            raise serializers.ValidationError(self.MESSAGE_TOO_MANY_COUNTRIES)
        return value


def _date_format(string):
    try:
        return datetime.strptime(string[0:10], '%Y-%m-%d').strftime('%d %b %Y')
    except Exception:
        return ''


def parse_opportunities(results):
    return [
        {
            'title': result['title'],
            'description': Truncator(result['description']).chars(30),
            'source': result['source'],
            'url': result['url'],
            'published_date': _date_format(result['published_date']),
            'closing_date': _date_format(result['closing_date']),
        }
        for result in results
    ]
