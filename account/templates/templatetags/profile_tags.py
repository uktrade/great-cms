import datetime

from django.template import Library

register = Library()


@register.filter(expects_localtime=True)
def parse_date(value, date_format):
    return datetime.datetime.strptime(value, date_format)
