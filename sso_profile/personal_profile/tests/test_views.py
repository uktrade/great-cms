from unittest import mock

from django.urls import reverse


def test_personal_profile_edit_existing_profile(client, mock_update_user_profile, user_with_profile):
    client.force_login(user_with_profile)
    data = {'given_name': 'Foo', 'family_name': 'Example', 'job_title': 'Exampler', 'phone_number': '1232342'}

    response = client.get(reverse('personal-profile:edit'))

    assert response.status_code == 200

    response = client.post(reverse('personal-profile:edit'), data)

    assert response.status_code == 302
    assert response.url == reverse('personal-profile:display')
    assert mock_update_user_profile.call_count == 1
    assert mock_update_user_profile.call_args == mock.call(
        sso_session_id=user_with_profile.session_id,
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
    )


def test_personal_profile_edit_no_profile(client, mock_create_user_profile, user):
    client.force_login(user)
    data = {'given_name': 'Foo', 'family_name': 'Example', 'job_title': 'Exampler', 'phone_number': '1232342'}

    response = client.get(reverse('personal-profile:edit'))

    assert response.status_code == 200

    response = client.post(reverse('personal-profile:edit'), data)

    assert response.status_code == 302
    assert response.url == reverse('personal-profile:display')
    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        sso_session_id=user.session_id,
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
    )
