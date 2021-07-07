from directory_components import forms


class PersonalProfileEdit(forms.Form):
    given_name = forms.CharField(label='First name')
    family_name = forms.CharField(label='Last name')
    job_title = forms.CharField(label='Job title')
    phone_number = forms.CharField(label='Telephone number (optional)', required=False)
