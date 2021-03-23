from unittest.mock import patch

import pytest
from django.urls import reverse

from exportplan import forms
from exportplan.core import helpers


@pytest.fixture
def about_your_business_form_data():
    return {
        'story': 'Lorem ipsum',
        'location': 'Dolor sit amet',
        'processes': 'Consectetur adipisicing elit',
        'packaging': 'Sed do eiusmod tempor',
    }


@pytest.fixture
def target_markets_research_data():
    return {
        'demand': 'Lorem ipsum',
        'competitors': 'Dolor sit amet',
        'trend': 'Consectetur adipisicing elit',
        'unqiue_selling_proposition': 'Sed do eiusmod tempor',
        'average_price': 10,
    }


@pytest.fixture
def objectives_form_data():
    return {
        'objectives': {
            'rationale': 'Lorem ipsum',
        }
    }


def test_about_your_business_form_valid(about_your_business_form_data):
    form = forms.ExportPlanAboutYourBusinessForm(data=about_your_business_form_data)
    assert form.is_valid()


def test_about_your_business_form_missing_fields():
    form = forms.ExportPlanAboutYourBusinessForm(
        data={
            'story': 'Lorem ipsum',
            'location': 'Dolor sit amet',
        }
    )
    assert form.is_valid()


def test_about_your_business_form_empty_fields():
    form = forms.ExportPlanAboutYourBusinessForm(
        data={
            'story': '',
            'location': '',
            'processes': '',
            'packaging': '',
        }
    )
    assert form.is_valid()


def test_target_markets_research_form_valid(target_markets_research_data):
    form = forms.ExportPlanAboutYourBusinessForm(data=target_markets_research_data)
    assert form.is_valid()


def test_target_markets_research_missing_fields():
    form = forms.ExportPlanAboutYourBusinessForm(
        data={
            'demand': 'Lorem ipsum',
            'competitors': 'Dolor sit amet',
        }
    )
    assert form.is_valid()


def test_target_markets_research_form_empty_fields():
    form = forms.ExportPlanTargetMarketsResearchForm(
        data={
            'demand': '',
            'competitors': '',
            'trend': '',
            'unqiue_selling_proposition': '',
            'average_price': None,
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_about_your_business_form_view(
    export_plan_data, about_your_business_form_data, client, user, mock_get_user_profile
):
    export_plan_data['about_your_business'] = about_your_business_form_data
    url = reverse('exportplan:about-your-business')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
@patch.object(helpers, 'get_cia_world_factbook_data')
@patch.object(helpers, 'get_or_create_export_plan')
def test_market_markets_research_form_view(
    mock_get_export_plan,
    mock_cia_factbook_data,
    mock_get_comtrade_data,
    target_markets_research_data,
    client,
    user,
    mock_get_user_profile,
):
    mock_get_export_plan.return_value = {
        'pk': 1,
        'target_markets_research': target_markets_research_data,
        'export_countries': [{'country_name': 'Netherlands'}],
    }
    url = reverse('exportplan:target-markets-research')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


def test_objectives_form_empty_fields():
    form = forms.ExportPlanAboutYourBusinessForm(
        data={
            'rational': '',
        }
    )
    assert form.is_valid()
