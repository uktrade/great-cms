import pytest

from core.fern import Fern


@pytest.mark.django_db
def test_fern():
    text = 'Cras aliquam neque consectetur'
    enc = Fern().encrypt(text)
    dec = Fern().decrypt(enc)
    assert text, dec
