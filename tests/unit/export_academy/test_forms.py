from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from export_academy.forms import (
    BoolToDateTimeField,
    EARegistration,
    EventAdminModelForm,
)
from export_academy.models import Event


def test_registration_form_validations(valid_registration_form_data):
    form = EARegistration(data=valid_registration_form_data)

    assert form.is_valid()
    assert form.cleaned_data['first_name'] == valid_registration_form_data['first_name']
    assert form.cleaned_data['business_name'] == valid_registration_form_data['business_name']
    assert form.cleaned_data.items() <= form.serialized_data.items()
    assert form.serialized_data['like_to_discuss_country'] == 'Italy'


@freeze_time('2023-01-01 01:00:00')
def test_custom_field_converts_boolean_to_datetime():
    field = BoolToDateTimeField()

    assert field.to_python(True) == timezone.now()
    assert field.to_python(False) is None


def test_event_admin_form_keeps_initial_values():
    EventAdminModelForm._meta.model = Event  # type: ignore
    EventAdminModelForm.formsets = {}  # type: ignore

    now = timezone.now()
    later = now + timedelta(hours=1)

    form = EventAdminModelForm()
    form['completed'].initial = now
    form['live'].initial = now
    form.cleaned_data = {'completed': later, 'live': later}

    assert form.clean_completed() == now
    assert form.clean_live() == now


def test_event_admin_form_keeps_new_values():
    EventAdminModelForm._meta.model = Event  # type: ignore
    EventAdminModelForm.formsets = {}  # type: ignore

    now = timezone.now()

    form = EventAdminModelForm()
    form['completed'].initial = None
    form['live'].initial = None
    form.cleaned_data = {'completed': now, 'live': now}

    assert form.clean_completed() == now
    assert form.clean_live() == now
