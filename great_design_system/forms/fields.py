from captcha.fields import ReCaptchaField  # noqa
from django import forms
from django.core import validators
from django.forms.boundfield import BoundField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


def validate_day_month_year_is_within_range(value):

    year, month, day = value.split('-')
    errors = []
    try:
        day = int(day)
        if day < 1 or day > 31:
            errors.append(f'"{day}" is not between 1 and 31')
        month = int(month)
        if month < 1 or month > 12:
            errors.append(f'"{month}" is not between 1 and 12')
        year = int(year)
        if year <= 2025:
            errors.append(f'"{year}" must be a number equals to or above 2025')
    except ValueError:
        # will default to built in message
        pass
    if errors:
        raise ValidationError(errors)

    
def validate_month_is_within_range(value):
    try:
        value = int(value)
        if value < 1 or value > 12:
            raise ValidationError(f'"{value}" is not between 1 and 12', params={'value': value})
    except ValueError:
        raise ValidationError(f'"{value}" must be a number between 1 and 12', params={'value': value})
    
def validate_year_is_within_range(value):
    try:
        value = int(value)
        if value >= 2025:
            raise ValidationError('Year can not be in the past', params={'value': value})
    except ValueError:
        raise ValidationError(f'"{value}" must be a number equals to or above 2025', params={'value': value})

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
        return self.field.attrs

    def help_text_css_classes(self):
        """
        Return a string of space-separated CSS classes for this field.
        """
        return f'{self.field.widget.help_text_class_name} govuk-hint'

    @property
    def id_for_container(self):
        return f'id_{self.name}_container'

    @property
    def is_page_heading(self):
        return self.field.is_page_heading

    @property
    def legend(self):
        if self.use_fieldset:
            return {'isPageHeading': self.is_page_heading, 'text': self.label}
        return {}


class GDSFieldMixin:
    def __init__(
        self,
        is_page_heading=False,
        exclusive_choice='None',
        linked_conditional_reveal=None,
        linked_conditional_reveal_fields=[],
        linked_conditional_reveal_choice='yes',
        hide_on_page_load=False,
        counter=False,
        min_length=None,
        max_length=None,
        max_words=None,
        threshold=None,
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
        self.is_page_heading = is_page_heading
        self.hide_on_page_load = hide_on_page_load
        self.counter = counter
        self.max_length = max_length
        self.max_words = max_words
        self.threshold = threshold
        self.choice_help_text = choice_help_text

        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(int(min_length)))
        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(int(max_length)))

    @property
    def container_css_classes(self):
        widget_class = getattr(self.widget, 'container_css_classes', '')

        # This is helpful on forms where we need hide/show logic
        # show_on_page_load will always be added to form-groups as default
        # hide_on_page_load will be used on form groups that will not display until criteria is met.
        page_load_class = 'great-hidden' if self.hide_on_page_load else ''

        counter_class = 'govuk-character-count' if self.counter else ''

        return f'{self._container_css_classes} {widget_class} {page_load_class} {counter_class}'

    @property
    def attrs(self):
        attr_dict = {}
        if self.counter:
            attr_dict.update({'data-module': 'govuk-character-count'})
        if self.max_length > 0:
            attr_dict.update({'data-maxlength': self.max_length})
        if self.max_words > 0:
            attr_dict.update({'data-maxwords': self.max_words})
        if self.threshold > 0:
            attr_dict.update({'data-threshold': self.threshold})
        return attr_dict

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
BooleanField = field_factory(forms.BooleanField)


class ReCaptchaField(ReCaptchaField):
    pass


class TypeDateField(DateField):

    def clean(self, value):
        """
        Run the bespoke day, month & year validation
        """
        validate_day_month_year_is_within_range(value)
        return super().clean(value)
