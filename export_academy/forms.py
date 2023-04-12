from datetime import datetime

from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.forms import CheckboxInput, DateTimeField, HiddenInput, Select, Textarea
from django.forms.widgets import ChoiceWidget
from django.utils.translation import gettext_lazy as _
from great_components import forms
from wagtail.admin.forms import WagtailAdminModelForm

from contact.forms import TERMS_LABEL
from directory_constants.choices import COUNTRY_CHOICES

COUNTRIES = COUNTRY_CHOICES.copy()
COUNTRIES.insert(0, ('', 'Select a country'))


class ChoiceSubmitButtonWidget(ChoiceWidget):
    """ChoiceSubmitButtonWidget renders choices as multiple 'submit' type buttons"""

    input_type = 'submit'
    template_name = 'export_academy/widgets/submit.html'
    option_template_name = 'export_academy/widgets/submit_option.html'
    checked_attribute = {'disabled': True}


class BoolToDateTimeField(DateTimeField):
    widget = CheckboxInput

    def to_python(self, value):
        value = datetime.now().isoformat() if value else ''
        return super().to_python(value)


class EARegistration(GovNotifyEmailActionMixin, forms.Form):
    first_name = forms.CharField(
        label=_('Given name'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your name'),
        },
    )
    last_name = forms.CharField(
        label=_('Surname'),
        min_length=2,
        max_length=50,
        error_messages={
            'required': _('Enter your family name'),
        },
    )
    job_title = forms.CharField(
        label=_('Job title'),
        max_length=50,
        error_messages={
            'required': _('Enter your job title'),
        },
    )
    business_name = forms.CharField(
        label=_('Business name'),
        max_length=50,
        error_messages={
            'required': _('Enter your business name'),
        },
    )
    business_website = forms.CharField(
        label=_('Business website'),
        max_length=255,
        error_messages={
            'required': _(
                'Enter a website address in the correct format, like https://www.example.com or www.company.com'
            ),
            'invalid': _(
                'Enter a website address in the correct format, like https://www.example.com or www.company.com'
            ),
        },
        required=False,
    )
    country = forms.ChoiceField(
        label=_('Drop down example'),
        widget=Select(),
        choices=COUNTRIES,
    )
    like_to_discuss = forms.ChoiceField(
        label=_('Radio button example'),
        choices=(
            ('no', 'No'),
            ('yes', 'Yes'),
        ),
        widget=forms.RadioSelect,
        error_messages={'required': _('Please answer this question')},
    )
    like_to_discuss_other = forms.ChoiceField(
        label=_('Which country is the project located in?'),
        widget=Select(),
        choices=COUNTRIES,
        required=False,
    )
    how_can_we_help = forms.CharField(
        label=_('How can we help?'),
        help_text=_('Text area example'),
        widget=Textarea,
    )
    terms_agreed = forms.BooleanField(
        label=TERMS_LABEL,
        error_messages={
            'required': _('You must agree to the terms and conditions' ' before registering'),
        },
    )

    @property
    def serialized_data(self):
        data = super().serialized_data
        countries_mapping = dict(COUNTRY_CHOICES)
        country_label = countries_mapping.get(data['country'])
        data['country_label'] = country_label
        data['like_to_discuss_country'] = ''
        if data.get('like_to_discuss') == 'yes':
            data['like_to_discuss_country'] = countries_mapping.get(data['like_to_discuss_other'])
        return data


class EventAdminModelForm(WagtailAdminModelForm):
    completed = BoolToDateTimeField(widget=CheckboxInput, required=False)
    live = BoolToDateTimeField(widget=HiddenInput, required=False)

    def _clean_field(self, fieldname):
        """Obtains new value if there is no initial value in the DB"""
        initial_value = self[fieldname].initial
        data_value = self.cleaned_data[fieldname]
        if initial_value and data_value is not None:
            return initial_value

        return data_value

    def clean_completed(self):
        return self._clean_field('completed')

    def clean_live(self):
        return self._clean_field('live')

    def _clean_live_event(self, field):
        event_format = self.cleaned_data.get('format')
        field_value = self.cleaned_data.get(field)
        if event_format == self.Meta.model.IN_PERSON:
            if not field_value:
                self._errors[field] = self.error_class(['In-person event requires this field.'])

        return field_value

    def clean_cut_off_days(self):
        return self._clean_live_event('cut_off_days')

    def clean_max_capacity(self):
        return self._clean_live_event('max_capacity')
