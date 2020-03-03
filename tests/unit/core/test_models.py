from unittest import mock

from core.models import AbstractObjectHash


def test_object_hash():
    mocked_file = mock.Mock()
    mocked_file.read.return_value = b'foo'
    hash = AbstractObjectHash.generate_content_hash(mocked_file)
    assert hash == 'acbd18db4cc2f85cedef654fccc4a4d8'
