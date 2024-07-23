from unittest import mock

import pytest

from export_academy.wagtail_hooks import EventAdmin, EventAdminButtonHelper
from tests.unit.export_academy.factories import EventFactory


@pytest.mark.django_db
def test_event_admin_button_helper(rf, django_user_model):
    obj = EventFactory()

    user = django_user_model.objects.create_user(
        username='username',
        password='password',
        is_staff=True,
    )

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
        {
            'url': '/admin/mock-url/path/',
            'label': 'Inspect',
            'classname': 'button button-secondary',
            'title': 'Inspect this event',
        },
        {
            'url': '/admin/mock-url/path/',
            'label': 'Clone',
            'classname': 'button button-small button-secondary',
            'title': 'Clone a new event',
        },
        {
            'url': '/admin/mock-url/path/',
            'label': 'Edit',
            'classname': 'button button-secondary',
            'title': 'Edit this event',
        },
        {'url': '/admin/mock-url/path/', 'label': 'Delete', 'classname': 'button no', 'title': 'Delete this event'},
    ]


@pytest.mark.django_db
def test_event_admin(rf, django_user_model):
    admin = EventAdmin()
    obj_live = EventFactory()
    obj_draft = EventFactory(live=None)
    user = django_user_model.objects.create_user(
        username='username', password='password', is_staff=True, is_superuser=True
    )

    obj_live.types.add('Masterclass')  # type: ignore
    obj_live.types.add('Sector')  # type: ignore
    obj_draft.types.add('Market')  # type: ignore

    assert admin.get_types(obj_live) == 'Masterclass, Sector'
    assert admin.get_types(obj_draft) == 'Market'

    assert admin.get_status(obj_live) == 'LIVE'
    assert admin.get_status(obj_draft) == 'DRAFT'

    request = rf.get('/')
    request.user = user
    view = admin.clone_view(request, instance_pk=obj_live.pk)  # type: ignore

    assert view.context_data['model_admin'] == admin  # type: ignore
