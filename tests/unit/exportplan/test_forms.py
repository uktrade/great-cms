import pytest
from django.urls import reverse

from exportplan import forms


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
    url = reverse('exportplan:about-your-business', kwargs={'id': 1})
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
