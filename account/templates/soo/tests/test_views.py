from django.urls import reverse


def test_selling_online_overseas_exposes_context(client, user):
    client.force_login(user)
    url = reverse('selling-online-overseas')
    response = client.get(url)

    assert response.context_data['soo_tab_classes'] == 'active'
