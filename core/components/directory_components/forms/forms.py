from directory_constants.choices import COUNTRY_CHOICES

from django import forms
from django.conf import settings
from django.forms import Select
from django.template.loader import render_to_string
from django.utils import translation

from directory_components.forms import fields
from directory_components import helpers

__all__ = [
    'CountryForm',
    'DirectoryComponentsFormMixin',
    'Form',
    'get_country_form_initial_data',
    'get_language_form_initial_data',
    'LanguageForm',
]


BLANK_COUNTRY_CHOICE = [("", "Select a country")]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class DirectoryComponentsFormMixin:

    use_required_attribute = False
    error_css_class = 'form-group-error'

    def __str__(self):
        return render_to_string('directory_components/form_widgets/form.html', {'form': self})


class Form(DirectoryComponentsFormMixin, forms.Form):
    pass


class CountryForm(Form):
    country = fields.ChoiceField(
        label='Country',
        widget=Select(attrs={'id': 'great-header-country-select'}),
        choices=COUNTRIES
    )


def get_country_form_initial_data(request):
    return {
        'country': helpers.get_user_country(request).upper() or None
    }


class LanguageForm(forms.Form):
    lang = fields.ChoiceField(
        widget=Select(attrs={'id': 'great-header-language-select'}),
        choices=[]  # set by __init__
    )

    def __init__(self, language_choices=settings.LANGUAGES, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lang'].choices = language_choices

    def is_language_available(self, language_code):
        language_codes = [code for code, _ in self.fields['lang'].choices]
        return language_code in language_codes


def get_language_form_initial_data():
    return {
        'lang': translation.get_language()
    }
