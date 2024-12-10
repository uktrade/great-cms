# flake8: noqa
"""A home for regular expressions, so we don't reinvent the wheel"""

import re

NOT_NUMBERS_REGEX = re.compile(r'[^0-9]')
PHONE_NUMBER_REGEX = re.compile(r'^(\+\d{1,3}[- ]?)?\d{8,16}$')
PHONE_NUMBER_REGEX_SIGNUP = re.compile(r'^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?[\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$')
EMAIL_ADDRESS_REGEX = re.compile(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$')
