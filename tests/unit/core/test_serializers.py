import pytest

from core import serializers


@pytest.mark.parametrize(
    'string,expected',
    [
        ['', ''],
        ['2020-10-05', '05 Oct 2020'],
        ['2020-1-5', '05 Jan 2020'],
        ['2020-10--5', ''],
        ['2020-13-5', ''],
    ],
)
def test_date_format_serializer(string, expected):

    assert serializers._date_format(string) == expected
