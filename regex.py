"""A home for regular expressions, so we don't reinvent the wheel"""

import re

NOT_NUMBERS_REGEX = re.compile(r'[^0-9]')
PHONE_NUMBER_REGEX = re.compile(r'^(\+\d{1,3}[- ]?)?\d{8,16}$')
PHONE_NUMBER_REGEX_SIGNUP = re.compile(r'^[(+]*(?:[\s().-]*\d){9,15}$')
