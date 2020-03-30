from datetime import datetime
import markdown2
from bs4 import BeautifulSoup

from django.utils.text import Truncator
from rest_framework import serializers


class CompanySerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False)
    expertise_industries = serializers.JSONField(required=False)
    expertise_countries = serializers.JSONField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)


def _date_format(string):
    return datetime.strptime(string[0:10], '%Y-%m-%d').strftime('%d %b %Y')


def parse_opportunities(results):
    return [
        {
            'title': result['title'],
            'description': Truncator(result['description']).chars(30),
            'source': result['source'],
            'url': result['url'],
            'published_date': _date_format(result['published_date']),
            'closing_date': _date_format(result['closing_date'])
        }
        for result in results
    ]


def parse_events(results):

    def description(result):
        content = result.get('content', '')
        html = markdown2.markdown(content)
        stripped_content = ''.join(
            BeautifulSoup(html, 'html.parser').findAll(text=True)
        ).rstrip()
        return Truncator(stripped_content).chars(40)

    def location(result):
        if 'location' in result.keys() and 'city' in result['location'].keys():
            return result['location']['city']
        else:
            return 'n/a'

    def date(result):
        if 'date' in result.keys():
            return _date_format(result['date'])
        else:
            return 'n/a'

    return [
        {
            'title': result['name'],
            'description': description(result),
            'url': result['url'],
            'location': location(result),
            'date': date(result)
        }
        for result in results
    ]
