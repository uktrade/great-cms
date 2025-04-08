from captcha.fields import ReCaptchaField  # noqa
from django import forms
from django.forms.boundfield import BoundField


class GDSBoundField(BoundField):
    def label_tag(self, contents=None, attrs=None, label_suffix=None, tag=None):
        attrs = attrs or {}
        attrs['class'] = attrs.get('class', '') + ' govuk-label '
        return super().label_tag(contents=contents, attrs=attrs, label_suffix=label_suffix)

    def css_classes(self, *args, **kwargs):
        css_classes = super().css_classes(*args, **kwargs)

        if self.field.widget.input_type == 'password':
            css_classes = f'{css_classes} govuk-password-input'

        return f'{css_classes} {self.field.container_css_classes}'

    def field_attrs(self):
        attrs = {}
        if self.field.widget.input_type == 'password':
            attrs = {
                'data-module': 'govuk-password-input',
                'data-show-password-text': 'Show',
                'data-hide-password-text': 'Hide',
                'data-show-password-aria-label-text': 'Show password',
                'data-hide-password-aria-label-text': 'Hide password',
                'data-password-shown-announcement-text': 'Password shown',
                'data-password-hidden-announcement-text': 'Password Hidden',
            }
            data_module_attrs = self.field.widget.data_module_attrs
            attrs.update(**data_module_attrs)
        return attrs

    def help_text_css_classes(self):
        """
        Return a string of space-separated CSS classes for this field.
        """
        return f'{self.field.widget.help_text_class_name} govuk-hint'


class GDSFieldMixin:
    def __init__(
        self,
        exclusive_choice='None',
        linked_conditional_reveal=None,
        linked_conditional_reveal_fields=[],
        linked_conditional_reveal_choice='yes',
        hide_on_page_load=False,
        choice_help_text=[],
        container_css_classes='govuk-form-group',
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self._container_css_classes = container_css_classes
        self.widget.field = self
        self.widget.linked_conditional_reveal_fields = linked_conditional_reveal_fields
        self.widget.choice_help_text = choice_help_text
        self.linked_conditional_reveal = linked_conditional_reveal
        self.linked_conditional_reveal_fields = linked_conditional_reveal_fields
        self.linked_conditional_reveal_choice = linked_conditional_reveal_choice
        self.exclusive_choice = exclusive_choice
        self.hide_on_page_load = hide_on_page_load
        self.choice_help_text = choice_help_text

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')

        # This is helpful on forms where we need hide/show logic
        # show_on_page_load will always be added to form-groups as default
        # hide_on_page_load will be used on form groups that will not display until criteria is met.
        page_load_class = 'great-hidden' if self.hide_on_page_load else ''

        return f'{self._container_css_classes} {widget_class} {page_load_class}'

    def get_bound_field(self, form, field_name):
        return GDSBoundField(form, self, field_name)


def field_factory(base_class):
    bases = (GDSFieldMixin, base_class)
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
IntegerField = field_factory(forms.IntegerField)
GenericIPAddressField = field_factory(forms.GenericIPAddressField)
ImageField = field_factory(forms.ImageField)
MultipleChoiceField = field_factory(forms.MultipleChoiceField)
RegexField = field_factory(forms.RegexField)
SlugField = field_factory(forms.SlugField)
TimeField = field_factory(forms.TimeField)
TypedChoiceField = field_factory(forms.TypedChoiceField)
TypedMultipleChoiceField = field_factory(forms.TypedMultipleChoiceField)
URLField = field_factory(forms.URLField)
UUIDField = field_factory(forms.UUIDField)


class ReCaptchaField(ReCaptchaField):
    pass