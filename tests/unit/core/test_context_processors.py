import pytest

from django.shortcuts import reverse


@pytest.mark.django_db
def test_support_email_exists_in_template_context(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'great_support_email' in response.context
    assert response.context['great_support_email'] == 'great.support@trade.gov.uk'
