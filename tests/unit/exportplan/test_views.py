from django.urls import reverse


def test_export_plan_landing_page(client):
    url = reverse('exportplan:index')
    response = client.get(url)
    assert response.status_code == 200


def test_export_plan_builder_landing_page(client):
    url = reverse('exportplan:landing-page')
    response = client.get(url)
    assert response.status_code == 200


def test_export_plan_about_your_business(client):
    url = reverse('exportplan:about-your-business')
    response = client.get(url)
    assert response.status_code == 200
