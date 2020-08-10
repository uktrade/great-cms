import pytest

from core.fern import Fern


@pytest.mark.django_db
def test_valid_fern():
    text = 'Cras aliquam neque consectetur'
    enc = Fern().encrypt(text)
    dec = Fern().decrypt(enc)
    assert text, dec


@pytest.mark.django_db
def test_custom_key_fern(key='alpal'):
    text = 'Cras aliquam neque consectetur'
    enc = Fern().encrypt(text)
    assert enc is not None


@pytest.mark.django_db
def test_invalid_enc_fern(key='alpal'):
    text = 'Cras aliquam neque consectetur'
    enc = Fern().decrypt(text)
    assert enc == ''
