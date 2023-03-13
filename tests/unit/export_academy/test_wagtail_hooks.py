from unittest import mock

import pytest

from export_academy.wagtail_hooks import EventAdmin, EventAdminButtonHelper
from tests.unit.export_academy.factories import EventFactory


@pytest.mark.django_db
def test_event_admin_button_helper(rf, django_user_model):
    obj = EventFactory()

    user = django_user_model.objects.create_user(username='username', password='password', is_staff=True)

    request = rf.get('/')
    request.user = user

    mock_view = mock.Mock(name='mock_view')
    mock_view.model = obj._meta.model  # type: ignore
    mock_view.url_helper.get_action_url.return_value = '/admin/mock-url/path/'

    helper = EventAdminButtonHelper(request=request, view=mock_view)

    assert helper.clone_button(obj) == {
        'classname': 'button button-small button-secondary',
        'label': 'Clone',
        'title': 'Clone a new event',
        'url': '/admin/mock-url/path/',
    }

    assert helper.get_buttons_for_obj(obj) == [
        {'url': '/admin/mock-url/path/', 'label': 'Inspect', 'classname': 'button', 'title': 'Inspect this event'},
        {
            'url': '/admin/mock-url/path/',
            'label': 'Clone',
            'classname': 'button button-small button-secondary',
            'title': 'Clone a new event',
        },
        {'url': '/admin/mock-url/path/', 'label': 'Edit', 'classname': 'button', 'title': 'Edit this event'},
        {'url': '/admin/mock-url/path/', 'label': 'Delete', 'classname': 'button no', 'title': 'Delete this event'},
    ]


@pytest.mark.django_db
def test_event_admin(rf, django_user_model):
    admin = EventAdmin()
    obj = EventFactory()
    user = django_user_model.objects.create_user(username='username', password='password', is_staff=True)

    obj.types.add('Masterclass')  # type: ignore
    obj.types.add('Sector')  # type: ignore

    assert admin.get_types(obj) == 'Masterclass, Sector'

    request = rf.get('/')
    request.user = user
    view = admin.clone_view(request, instance_pk=obj.pk)  # type: ignore

    assert view.context_data['model_admin'] == admin  # type: ignore
