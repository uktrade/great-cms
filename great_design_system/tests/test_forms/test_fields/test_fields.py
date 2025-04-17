import pytest

from great_design_system import forms

field_classes = (
    forms.BooleanField,
    forms.CharField,
    forms.ChoiceField,
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
    forms.TypedDateField,
    forms.TypedMultipleChoiceField,
    forms.URLField,
    forms.UUIDField,
)


@pytest.mark.parametrize('field_class', field_classes)
def test_explicit_widget_attrs(field_class):
    field_explicit_attrs = field_class(widget=forms.TextInput(attrs={'class': 'test-class'}))
    assert field_explicit_attrs.widget.attrs['class'] == 'test-class'


@pytest.mark.parametrize('field_class', field_classes)
def test_container_class(field_class):
    class MyForm(forms.Form):
        field = field_class(container_css_classes='blah-blah')

    form = MyForm()

    assert form['field'].css_classes() == ' blah-blah   '
