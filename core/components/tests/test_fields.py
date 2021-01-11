import pytest

from django.forms import TextInput

from directory_components import forms


REQUIRED_MESSAGE = forms.PaddedCharField.default_error_messages['required']


class PaddedTestForm(forms.Form):
    field = forms.PaddedCharField(fillchar='0', max_length=6)


class RadioNestedForm(forms.BindNestedFormMixin, forms.Form):
    OTHER = 'OTHER'
    parent_field = forms.RadioNested(
        choices=[
            ('KG', 'Kilograms'),
            ('HANDS', 'Hands'),
            (OTHER, 'other')
        ],
        nested_form_class=PaddedTestForm,
        nested_form_choice=OTHER,
    )
    other_field = forms.CharField()


def test_padded_field_padds_value():
    form = PaddedTestForm(data={'field': 'val'})

    assert form.is_valid()
    assert form.cleaned_data['field'] == '000val'


def test_padded_field_handles_empty():
    for value in ['', None]:
        form = PaddedTestForm(data={'field': value})

        assert form.is_valid() is False
        assert form.errors['field'] == [REQUIRED_MESSAGE]


field_classes = (
    forms.CharField,
    forms.ChoiceField,
    forms.DateField,
    forms.DateTimeField,
    forms.DecimalField,
    forms.DurationField,
    forms.EmailField,
    forms.FileField,
    forms.FloatField,
    forms.GenericIPAddressField,
    forms.ImageField,
    forms.IntegerField,
    forms.MultipleChoiceField,
    forms.SlugField,
    forms.TimeField,
    forms.TypedChoiceField,
    forms.TypedMultipleChoiceField,
    forms.URLField,
    forms.UUIDField,
)


@pytest.mark.parametrize('field_class', field_classes)
def test_explicit_widget_attrs(field_class):
    field = field_class()

    field_explicit_attrs = field_class(
        widget=TextInput(attrs={'class': 'a-class'})
    )

    assert field.widget.attrs['class'] == ' form-control'
    assert field_explicit_attrs.widget.attrs['class'] == 'a-class form-control'


@pytest.mark.parametrize('field_class', field_classes)
def test_container_class(field_class):
    class MyForm(forms.Form):
        field = field_class(container_css_classes='border-purple')

    form = MyForm()

    assert form['field'].css_classes() == ' border-purple '


def test_radio_nested_form_validation():
    form = RadioNestedForm({
        'other_field': 'thing',
        'parent_field': 'KG',
    })
    assert form.is_valid()

    form = RadioNestedForm({
        'other_field': 'thing',
        'parent_field': RadioNestedForm.OTHER,
    })
    assert form.is_valid() is False
    assert 'parent_field' in form.errors
    assert 'field' in form.fields['parent_field'].nested_form.errors

    form = RadioNestedForm({
        'other_field': 'thing',
        'parent_field': RadioNestedForm.OTHER,
    })
    assert form.is_valid() is False
    assert 'parent_field' in form.errors
    assert 'field' in form.fields['parent_field'].nested_form.errors

    form = RadioNestedForm({
        'other_field': 'thing',
        'parent_field': RadioNestedForm.OTHER,
        'field': 'fooooo',
    })
    assert form.is_valid() is True
    assert form.cleaned_data == {
        'other_field': 'thing',
        'parent_field': RadioNestedForm.OTHER,
        'field': 'fooooo',
    }
