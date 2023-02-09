from export_academy.forms import EARegistration


def test_registration_form_validations(valid_registration_form_data):
    form = EARegistration(data=valid_registration_form_data)
    assert form.is_valid()
    assert form.cleaned_data['first_name'] == valid_registration_form_data['first_name']
    assert form.cleaned_data['business_name'] == valid_registration_form_data['business_name']
