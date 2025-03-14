from captcha.fields import ReCaptchaField # noqa
from django import forms
from django.forms.boundfield import BoundField

from gds_tooling.forms import widgets


class GDSBoundField(BoundField):
    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        attrs = attrs or {}
        attrs['class'] = attrs.get('class', '') + ' form-label'
        return super().label_tag(contents=contents, attrs=attrs, label_suffix=label_suffix)

    def css_classes(self, *args, **kwargs):
        css_classes = super().css_classes(*args, **kwargs)
        return f'{css_classes} {self.field.container_css_classes}'


class GDSFieldMixin:
    def __init__(self, hide_on_page_load=False, container_css_classes='form-group', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self._container_css_classes = container_css_classes
        self.widget.field = self
        self.hide_on_page_load = hide_on_page_load

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')
        return f'{self._container_css_classes} {widget_class}'

    def gds_dict_helper(self, obj, cls):
        gds_dict = {}
        if obj:
            gds_dict = {'text': obj}
            gds_dict['class'] = cls
            gds_dict['id'] = self.widget.id_for_label
        return gds_dict

    @property
    def gds_mapping(self):
        gds_dict = {
            'label': self.gds_dict_helper(self.label, self.label_css_classes),
            'hint': self.gds_dict_helper(self.help_text, self.hint_css_classes),
            'error': self.gds_dict_helper(self.error_messages, self.error_css_classes),
        }
        return gds_dict

    @property
    def label_css_classes(self):
        try:
            widget_defined_class = self.widget.attrs['label-class']
            if self.hide_on_page_load:
                return f'hide-on-page-load {widget_defined_class}'
            return self.widget.attrs['label-class']
        except KeyError:
            return ''

    @property
    def hint_css_classes(self):
        try:
            return self.widget.attrs['help-class']
        except KeyError:
            return ''

    @property
    def error_css_classes(self):
        try:
            return self.widget.attrs['error-class']
        except KeyError:
            return ''

    def get_bound_field(self, form, field_name):
        return GDSBoundField(form, self, field_name)


def field_factory(base_class):
    bases = (GDSFieldMixin, base_class)
    return type(base_class.__name__, bases, {})


GDSCharField = field_factory(forms.CharField)
GDSChoiceField = field_factory(forms.ChoiceField)
DateField = field_factory(forms.DateField)
DateTimeField = field_factory(forms.DateTimeField)
DecimalField = field_factory(forms.DecimalField)
DurationField = field_factory(forms.DurationField)
GDSEmailField = field_factory(forms.EmailField)
FileField = field_factory(forms.FileField)
FilePathField = field_factory(forms.FilePathField)
FloatField = field_factory(forms.FloatField)
GenericIPAddressField = field_factory(forms.GenericIPAddressField)
ImageField = field_factory(forms.ImageField)
GDSIntegerField = field_factory(forms.IntegerField)
MultipleChoiceField = field_factory(forms.MultipleChoiceField)
RegexField = field_factory(forms.RegexField)
SlugField = field_factory(forms.SlugField)
TimeField = field_factory(forms.TimeField)
TypedChoiceField = field_factory(forms.TypedChoiceField)
TypedMultipleChoiceField = field_factory(forms.TypedMultipleChoiceField)
URLField = field_factory(forms.URLField)
UUIDField = field_factory(forms.UUIDField)
class GDSReCaptchaField(ReCaptchaField):
    pass


class BooleanField(GDSFieldMixin, forms.BooleanField):
    widget = widgets.CheckboxWithInlineLabel

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')
        return widget_class

    def __init__(self, label='', help_text='', *args, **kwargs):
        super().__init__(label=label, *args, **kwargs)
        if isinstance(self.widget, widgets.CheckboxWithInlineLabel):
            self.widget.label = label
            self.widget.help_text = help_text
            self.label = ''


class GDSBooleanField(GDSFieldMixin, forms.BooleanField):
    widget = widgets.GDSCheckboxSelectInlineLabelMultiple

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')
        return widget_class

    def __init__(self, label='', help_text='', *args, **kwargs):
        super().__init__(label=label, *args, **kwargs)
        if isinstance(self.widget, widgets.GDSCheckboxSelectInlineLabelMultiple):
            self.widget.label = label
            self.widget.help_text = help_text
            self.label = ''
