import pytest
from unittest.mock import patch, call
from django.urls import reverse

from tests.helpers import create_response
from exportplan import forms, helpers


@pytest.fixture
def valid_form_data():
    return {
        'story': 'Lorem ipsum',
        'location': 'Dolor sit amet',
        'processes': 'Consectetur adipisicing elit',
        'packaging': 'Sed do eiusmod tempor',
    }


def test_brand_product_form_valid(valid_form_data):
    form = forms.ExportPlanBrandAndProductForm(
        data=valid_form_data
    )
    assert form.is_valid()


def test_brand_product_form_missing_fields():
    form = forms.ExportPlanBrandAndProductForm(
        data={
            'story': 'Lorem ipsum',
            'location': 'Dolor sit amet',
        }
    )
    assert form.is_valid()


def test_brand_product_form_empty_fields():
    form = forms.ExportPlanBrandAndProductForm(
        data={
            'story': '',
            'location': '',
            'processes': '',
            'packaging': '',
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
@patch.object(helpers, 'update_exportplan')
@patch.object(helpers, 'get_exportplan')
def test_brand_product_form_view(mock_get_export_plan, mock_update_exportplan, client, user):
    url = reverse('exportplan:brand-and-product')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
@patch.object(helpers, 'update_exportplan')
@patch.object(helpers, 'get_exportplan')
def test_brand_product_form_view_submission(
    mock_get_export_plan, mock_update_exportplan, valid_form_data, client, user
):
    url = reverse('exportplan:brand-and-product')
    client.force_login(user)
    response = client.post(url, valid_form_data)

    assert mock_update_exportplan.call_count == 1
    assert response.status_code == 302
    assert response.url == url
