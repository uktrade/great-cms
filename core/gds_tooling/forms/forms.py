from directory_constants.choices import COUNTRY_CHOICES

from django import forms
from django.conf import settings
from django.forms import Select
from django.template.loader import render_to_string
from django.utils import translation

from core.gds_tooling.forms import ChoiceField


BLANK_COUNTRY_CHOICE = [("", "Select a country")]
COUNTRIES = BLANK_COUNTRY_CHOICE + COUNTRY_CHOICES


class GDSFormMixin:

    use_required_attribute = False
    error_css_class = 'form-group-error'
    error_summary_heading = None

    def __str__(self):
        return render_to_string('form.html', {'form': self})


class Form(GDSFormMixin, forms.Form):
    pass


class LanguageForm(forms.Form):
    lang = ChoiceField(
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
