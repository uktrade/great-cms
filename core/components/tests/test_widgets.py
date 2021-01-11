from bs4 import BeautifulSoup
from directory_components import forms

TEST_CHOICES = (
    ('cyan', 'Cyan'),
    ('magenta', 'Magenta'),
    ('yellow', 'Yellow'),
)

TEST_CHOICES_WITH_SPACES = (
    ('cyan', 'Cyan colour'),
    ('magenta', 'Magenta colour'),
    ('yellow', 'Yellow colour'),
)


def test_checkbox_inline_label_widget():
    widget = forms.CheckboxWithInlineLabel(
        label='Box label', help_text='Help text', attrs={'id': 'checkbox_id', 'class': 'test-class'}
    )
    html = widget.render('name', 'value')
    soup = BeautifulSoup(html, 'html.parser')

    assert '<label ' in html
    assert '<span ' in html

    label = soup.find('label')
    assert label['for'] == 'checkbox_id'

    label_text = soup.select('span.form-label')[0]
    assert label_text.string == 'Box label'

    help_text = soup.select('span.form-hint')[0]
    assert help_text.string == 'Help text'


def test_checkbox_inline_label_multiple_widget():
    widget = forms.CheckboxSelectInlineLabelMultiple()
    html = widget.render('name', 'value')
    assert '<ul ' in html


def test_radio_select_widget():
    widget = forms.RadioSelect(attrs={'id': 'radio-test'}, choices=TEST_CHOICES)
    html = widget.render('name', 'value')
    soup = BeautifulSoup(html, 'html.parser')

    assert '<label ' in html
    assert '<ul ' in html

    list_element = soup.find('ul')
    assert list_element['id'] == 'radio-test'


def test_radio_nice_ids():
    widget = forms.RadioSelect(use_nice_ids=True, attrs={'id': 'radio-test'}, choices=TEST_CHOICES)
    html = widget.render('name', 'value')
    soup = BeautifulSoup(html, 'html.parser')

    list_items = soup.find_all('input')
    exp_ids = [
        'radio-test-cyan',
        'radio-test-magenta',
        'radio-test-yellow',
    ]
    for item, exp_id in zip(list_items, exp_ids):
        assert item.attrs['id'] == exp_id


def test_radio_default_ids():
    widget = forms.RadioSelect(attrs={'id': 'radio-test'}, choices=TEST_CHOICES)
    html = widget.render('name', 'value')
    soup = BeautifulSoup(html, 'html.parser')

    list_items = soup.find_all('input')
    exp_ids = [
        'radio-test_0',
        'radio-test_1',
        'radio-test_2',
    ]
    for item, exp_id in zip(list_items, exp_ids):
        assert item.attrs['id'] == exp_id


def test_radio_select_class_has_attrs():
    radio = forms.RadioSelect(attrs={'id': 'radio-test'})
    assert radio.input_type == 'radio'
    assert radio.css_class_name == 'select-multiple'
    assert radio.attrs['id'] == 'radio-test'


def test_checkbox_inline_class_has_attrs():
    checkbox = forms.CheckboxWithInlineLabel(label='Test label', help_text='Test helptext')
    context = checkbox.get_context('name', 'value', attrs=None)
    assert context['label'] == 'Test label'
    assert context['help_text'] == 'Test helptext'


def test_widget_id_handles_spaces_and_uppercase():
    widget = forms.RadioSelect(use_nice_ids=True, attrs={'id': 'radio-test'}, choices=TEST_CHOICES_WITH_SPACES)
    html = widget.render('name', 'value')
    soup = BeautifulSoup(html, 'html.parser')
    exp_ids = ['cyan-colour', 'magenta-colour', 'yellow-colour']

    inputs = soup.find_all('input')
    for input, exp_id in zip(inputs, exp_ids):
        assert input.attrs['id'] == 'radio-test-{}'.format(exp_id)
