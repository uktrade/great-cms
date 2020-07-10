import pytest

from django.contrib.auth.models import AnonymousUser

from . import factories
from core.fern import Fern
import unittest

from unittest.mock import patch, Mock

@pytest.mark.django_db
def test_fern():
    text = 'Cras aliquam neque consectetur'
    enc = Fern().encrypt(text)
    dec = Fern().decrypt(enc)
    assert(text, dec)
