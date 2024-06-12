import pytest

from django import forms

from find_a_buyer import validators

# https://github.com/django/django/blob/1.10/tests/validators/tests.py#L39
emails = [
    'email@here.com',
    'weirder-email@here.and.there.com',
    'email@[127.0.0.1]',
    'email@[2001:dB8::1]',
    'email@[2001:dB8:0:0:0:0:0:1]',
    'email@[::fffF:127.0.0.1]',
    'example@valid-----hyphens.com',
    'example@valid-with-hyphens.com',
    'test@domain.with.idn.tld.उदाहरण.परीक्षा',
    'email@localhost',
    '"test@test"@example.com',
    'example@atm.%s' % ('a' * 63),
    'example@%s.atm' % ('a' * 63),
    'example@%s.%s.atm' % ('a' * 63, 'b' * 10),
    '"\\\011"@here.com',
    'a@%s.us' % ('a' * 63),
]


def test_not_contain_email_does_contains_email():
    value_templates = [
        '{email} Thing',        # at the start
        '{email}Thing',         # at the start
        'Thing {email} Thing',  # middle
        'Thing{email}Thing',    # middle
        'Thing{email} Thing',   # middle
        'Thing{email}',         # at the end
        'Thing {email}',        # at the end
    ]
    for email in emails:
        for value_template in value_templates:
            value = value_template.format(email=email)
            with pytest.raises(forms.ValidationError):
                validators.does_not_contain_email(value)


def test_not_contain_email_does_not_contain_email():
    assert validators.does_not_contain_email('Thing') is None
    assert validators.does_not_contain_email('') is None
