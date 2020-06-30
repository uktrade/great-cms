import pytest
from unittest.mock import patch
from django.urls import reverse

from exportplan import forms, helpers


@pytest.fixture
def brand_product_form_data():
    return {
        'story': 'Lorem ipsum',
        'location': 'Dolor sit amet',
        'processes': 'Consectetur adipisicing elit',
        'packaging': 'Sed do eiusmod tempor',
    }


@pytest.fixture
def objectives_form_data():
    return {
        'rational': 'Lorem ipsum',
    }


def test_brand_product_form_valid(brand_product_form_data):
    form = forms.ExportPlanBrandAndProductForm(
        data=brand_product_form_data
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
@patch.object(helpers, 'get_or_create_export_plan')
def test_brand_product_form_view(mock_get_export_plan, mock_update_exportplan, brand_product_form_data, client, user):
    mock_get_export_plan.return_value = {'pk': 1, 'brand_product_details': brand_product_form_data}
    url = reverse('exportplan:brand-and-product')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
@patch.object(helpers, 'update_exportplan')
@patch.object(helpers, 'get_or_create_export_plan')
def test_brand_product_form_view_submission(
    mock_get_export_plan, mock_update_exportplan, brand_product_form_data, client, user
):
    url = reverse('exportplan:brand-and-product')
    client.force_login(user)
    response = client.post(url, brand_product_form_data)

    assert mock_update_exportplan.call_count == 1
    assert response.status_code == 302
    assert response.url == url


def test_objectives_form_valid(objectives_form_data):
    form = forms.ExportPlanBusinessObjectivesForm(
        data=objectives_form_data
    )
    assert form.is_valid()


def test_objectives_form_missing_fields():
    form = forms.ExportPlanBusinessObjectivesForm(
        data={}
    )
    assert form.is_valid()


def test_objectives_form_empty_fields():
    form = forms.ExportPlanBrandAndProductForm(
        data={
            'rational': '',
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
@patch.object(helpers, 'update_exportplan')
@patch.object(helpers, 'get_or_create_export_plan')
def test_objectives_form_view(mock_get_export_plan, mock_update_exportplan, objectives_form_data, client, user):
    mock_get_export_plan.return_value = {
        'pk': 1,
        **objectives_form_data,
        'company_objectives': [],
    }
    url = reverse('exportplan:objectives')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
@patch.object(helpers, 'update_exportplan')
@patch.object(helpers, 'get_or_create_export_plan')
def test_objectives_form_view_submission(
    mock_get_export_plan, mock_update_exportplan, objectives_form_data, client, user
):
    url = reverse('exportplan:objectives')
    client.force_login(user)
    response = client.post(url, objectives_form_data)

    assert mock_update_exportplan.call_count == 1
    assert response.status_code == 302
    assert response.url == url
