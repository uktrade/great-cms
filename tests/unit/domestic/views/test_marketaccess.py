import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_form_feature_flag_off(client, settings):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = False

    response = client.get(reverse('domestic:market-access'))

    assert response.status_code == 404


def test_form_feature_flag_on(client, settings):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = True

    response = client.get(reverse('domestic:market-access'))

    assert response.status_code == 200
