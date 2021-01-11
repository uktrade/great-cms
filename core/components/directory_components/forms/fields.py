from django import forms
from django.forms.boundfield import BoundField

from directory_components.forms import widgets


__all__ = [
    'DirectoryComponentsFieldMixin',
    'BindNestedFormMixin',
    'DirectoryComponentsBoundField',
    'field_factory',
    'PaddedCharField',
    'RadioNested',
    'BooleanField',
    'CharField',
    'ChoiceField',
    'DateField',
    'DateTimeField',
    'DecimalField',
    'DurationField',
    'EmailField',
    'FileField',
    'FilePathField',
    'FloatField',
    'GenericIPAddressField',
    'ImageField',
    'IntegerField',
    'MultipleChoiceField',
    'RegexField',
    'SlugField',
    'TimeField',
    'TypedChoiceField',
    'TypedMultipleChoiceField',
    'URLField',
    'UUIDField',
]


class BindNestedFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, RadioNested):
                nested_form = field.nested_form_class(*args, **kwargs)
                # require the nested fields to be provided if the parent field is checked
                if field.coerce(self[name].data) != field.nested_form_choice:
                    for item in nested_form.fields.values():
                        item.required = False
                field.bind_nested_form(nested_form)

    def clean(self):
        super().clean()
        for field_name in list(self.cleaned_data.keys()):
            field = self.fields[field_name]
            if isinstance(field, RadioNested) and field.nested_form.is_valid():
                self.cleaned_data.update(field.nested_form.cleaned_data)


class DirectoryComponentsBoundField(BoundField):
    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = attrs.get('class', '') + ' form-label'
        return super().label_tag(
            contents=contents,
            attrs=attrs,
            label_suffix=label_suffix
        )

    def css_classes(self, *args, **kwargs):
        css_classes = super().css_classes(*args, **kwargs)
        return f'{css_classes} {self.field.container_css_classes}'


class DirectoryComponentsFieldMixin:

    def __init__(self, container_css_classes='form-group', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self.widget, 'css_class_name'):
            self.widget.attrs['class'] = self.widget.attrs.get('class', '') + ' form-control'
        self.label_suffix = ''
        self._container_css_classes = container_css_classes

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')
        return f'{self._container_css_classes} {widget_class}'

    def get_bound_field(self, form, field_name):
        return DirectoryComponentsBoundField(form, self, field_name)


def field_factory(base_class):
    bases = (DirectoryComponentsFieldMixin, base_class)
    return type(base_class.__name__, bases, {})


CharField = field_factory(forms.CharField)
ChoiceField = field_factory(forms.ChoiceField)
DateField = field_factory(forms.DateField)
DateTimeField = field_factory(forms.DateTimeField)
DecimalField = field_factory(forms.DecimalField)
DurationField = field_factory(forms.DurationField)
EmailField = field_factory(forms.EmailField)
FileField = field_factory(forms.FileField)
FilePathField = field_factory(forms.FilePathField)
FloatField = field_factory(forms.FloatField)
GenericIPAddressField = field_factory(forms.GenericIPAddressField)
ImageField = field_factory(forms.ImageField)
IntegerField = field_factory(forms.IntegerField)
MultipleChoiceField = field_factory(forms.MultipleChoiceField)
RegexField = field_factory(forms.RegexField)
SlugField = field_factory(forms.SlugField)
TimeField = field_factory(forms.TimeField)
TypedChoiceField = field_factory(forms.TypedChoiceField)
TypedMultipleChoiceField = field_factory(forms.TypedMultipleChoiceField)
URLField = field_factory(forms.URLField)
UUIDField = field_factory(forms.UUIDField)


class BooleanField(DirectoryComponentsFieldMixin, forms.BooleanField):
    widget = widgets.CheckboxWithInlineLabel

    def __init__(self, label='', help_text='', *args, **kwargs):
        super().__init__(label=label, *args, **kwargs)
        if isinstance(self.widget, widgets.CheckboxWithInlineLabel):
            self.widget.label = label
            self.widget.help_text = help_text
            self.label = ''


class PaddedCharField(CharField):
    def __init__(self, fillchar, *args, **kwargs):
        self.fillchar = fillchar
        super().__init__(*args, **kwargs)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value not in self.empty_values:
            return value.rjust(self.max_length, self.fillchar)
        return value


class RadioNested(TypedChoiceField):
    MESSAGE_FORM_MIXIN = 'This field requires the form to use BindNestedFormMixin'
    widget = widgets.RadioNestedWidget

    def __init__(self, nested_form_class=None, nested_form_choice=True, *args, **kwargs):
        self.nested_form_class = nested_form_class
        self.nested_form_choice = nested_form_choice
        super().__init__(*args, **kwargs)
        self.widget.nested_form_choice = nested_form_choice

    def bind_nested_form(self, form):
        self.nested_form = form
        self.widget.bind_nested_form(form)

    def validate(self, value):
        super().validate(value)
        if value and not self.nested_form.is_valid():
            # trigger the form to mark the field as invalid. the nested form will then render the real errors
            raise forms.ValidationError(message='')

    def get_bound_field(self, form, field_name):
        assert isinstance(form, BindNestedFormMixin), self.MESSAGE_FORM_MIXIN
        return super().get_bound_field(form, field_name)
