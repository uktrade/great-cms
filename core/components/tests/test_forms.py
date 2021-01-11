from bs4 import BeautifulSoup

from django.forms import HiddenInput
from django.utils import translation

from directory_components import forms


def test_get_language_form_initial_data():
    with translation.override('fr'):
        data = forms.get_language_form_initial_data()
        assert data['lang'] == 'fr'


def test_form_render():
    class Form(forms.Form):
        field = forms.CharField()

    form = Form()

    expected = """
        <div class=" form-group" id="id_field-container">
            <label class=" form-label" for="id_field">Field</label>
            <input type="text" name="field" class=" form-control" id="id_field">
        </div>
    """

    actual = str(form)

    assert BeautifulSoup(actual, 'html.parser') == BeautifulSoup(expected, 'html.parser')


def test_form_render_hidden():
    class Form(forms.Form):
        field_one = forms.CharField()
        field_two = forms.CharField(widget=HiddenInput())

    form = Form()

    expected = """
        <div class=" form-group" id="id_field_one-container">
            <label class=" form-label" for="id_field_one">Field one</label>
            <input type="text" name="field_one" class=" form-control" id="id_field_one">
        </div>
        <input type="hidden" name="field_two" class=" form-control" id="id_field_two">
    """

    actual = str(form)

    assert BeautifulSoup(actual, 'html.parser') == BeautifulSoup(expected, 'html.parser')
