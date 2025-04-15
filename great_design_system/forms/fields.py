import datetime

from captcha.fields import ReCaptchaField  # noqa
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.boundfield import BoundField
from django.forms.utils import pretty_name

from great_design_system.forms.widgets import TypedDateWidget


class GDSBoundField(BoundField):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if self.field.label is None:
            self.field.name = pretty_name(self.name)
        else:
            self.field.name = self.field.label

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
        name=None,
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
        self.name = name
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


class TypedDateField(DateField):

    widget = TypedDateWidget
    DAY_LOW_HIGH_THRESHOLD = [1, 31]
    MONTH_LOW_HIGH_THRESHOLD = [1, 12]
    subwidget_error_class = 'govuk-input--error'

    def __init__(
        self,
        accept_future=True,
        accept_past=True,
        accept_today=True,
        date_thresholds=[],  # ['dd/mm/yyyy', 'dd/mm/yyyy'] or ['dd/mm/yyyy']
        accept_match_date_threshold=True,
        accept_before_date_threshold=True,
        accept_above_date_threshold=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # datefield will check valid dates against these kwarg
        # given dates can be in the future
        self.accept_future = accept_future
        # given dates can be in the past
        self.accept_past = accept_past
        # given dates can be today
        self.accept_today = accept_today
        # list of 1 or 2 dates.
        self.date_thresholds = date_thresholds
        # given date can be before date threshold
        self.accept_before_date_threshold = accept_before_date_threshold
        # given date can be after date threshold
        self.accept_above_date_threshold = accept_above_date_threshold
        # given date can be between the date_thresholds
        self.accept_match_date_threshold = accept_match_date_threshold

    def converted_date_str(self, string, date_type):
        is_wrong_format_string = f'{self.name} must be a real date.'

        date_dict = {
            'date': string,
            'type': date_type,
            'error': [f'{self.label} must include a valid {date_type}'],
            'is_blank_string': '',
            'exceeds_high_threshold': False,
            'below_low_threshold': False,
            'is_wrong_format_string': '',
        }
        try:
            date = int(string)
        except ValueError:
            date_dict.update({'is_wrong_format_string': is_wrong_format_string})
            return date_dict

        if type(date) is int:
            date_dict.update({'date': date, 'error': []})

            # Wrong format examples:
            # 1: day = 'T'
            # 2: day = '32'
            # 3: month = '13'
            # 3: year = '200'
            # 4: year = '20251'
            incorrect_year_format = False if date_type == 'year' and len(str(date)) != 4 else True
            incorrect_day_format = (
                False
                if date_type == 'day'
                and (date < self.DAY_LOW_HIGH_THRESHOLD[0] or date > self.DAY_LOW_HIGH_THRESHOLD[1])
                else True
            )
            incorrect_month_format = (
                False
                if date_type == 'month'
                and (date < self.MONTH_LOW_HIGH_THRESHOLD[0] or date > self.MONTH_LOW_HIGH_THRESHOLD[1])
                else True
            )
            if any([incorrect_year_format is False, incorrect_day_format is False, incorrect_month_format is False]):
                date_dict.update({'is_wrong_format_string': is_wrong_format_string})

        # Check for blank date fields
        # We catch the 'all fields missing' corner case in the gds_validation method
        if any([date == '', date == 0, date == '0']):
            date_dict.update({'is_blank_string': date_dict['type']})

        return date_dict

    def _past_present_future(self, date, today, errors, error_dict, error_string_start):

        error_combinations = {
            'before': 'in the past',
            'current': 'today',
            'after': 'in the future',
            'current_and_before': 'today or in the past',
            'current_and_after': 'today or in the future',
        }

        error_end = self._get_date_error(
            date, today, self.accept_past, self.accept_today, self.accept_future, error_combinations
        )

        if error_end:
            errors = [f'{error_string_start} {error_end}.', error_dict]
        return errors

    def _get_date_error(self, date, date_marker, before, current, after, error_combinations):
        if date == date_marker:
            if not current:
                return error_combinations['after'] if not before else error_combinations['before']
            return None

        if not after and not before and current:
            return error_combinations['current']

        if date < date_marker and not before:
            return error_combinations['current_and_after'] if current else error_combinations['after']

        if date > date_marker and not after:
            return error_combinations['current_and_before'] if current else error_combinations['before']

        return None

    def _date_threshold(self, thresholds, date, errors, error_dict, error_string_start):

        pretty_low_date = thresholds[0].strftime('%d %B %Y')
        pretty_high_date = '' if len(thresholds) == 1 else thresholds[1].strftime('%d %B %Y')

        error_combinations = {
            'before': f'before {pretty_low_date}',
            'current': pretty_low_date,
            'after': f'after {pretty_low_date}',
            'current_and_before': f'the same as or before {pretty_low_date}',
            'current_and_after': f'the same as or after {pretty_low_date}',
            'between': f'between {pretty_low_date} and {pretty_high_date}',
        }

        error_end = self._get_date_error(
            date,
            thresholds[0],
            self.accept_before_date_threshold,
            self.accept_match_date_threshold,
            self.accept_above_date_threshold,
            error_combinations,
        )

        # Corner case - If the given date must be between 2 dates
        if len(thresholds) == 2:
            low = thresholds[0]
            high = thresholds[1]
            if date < low or date > high:
                error_end = error_combinations['between']
        if error_end:
            errors = [f'{error_string_start} {error_end}.', error_dict]

        return errors

    def gds_validation_on_valid_date_string(self, value):

        error_string_start = f'{self.name} must be'
        error_dict = {
            'day': self.subwidget_error_class,
            'month': self.subwidget_error_class,
            'year': self.subwidget_error_class,
        }
        errors = ['', {'day': '', 'month': '', 'year': ''}]

        if value is None:
            return errors

        today = datetime.datetime.today().date()
        date = self.strptime(value, '%d/%m/%Y')

        # this may need sorting to ensure lowest date is index 0
        thresholds = [self.strptime(threshold, '%d/%m/%Y') for threshold in self.date_thresholds]
        thresholds.sort()

        # Work through past, present and future logic
        if any([self.accept_past is False, self.accept_today is False, self.accept_future is False]):
            errors = self._past_present_future(date, today, errors, error_dict, error_string_start)
        # Work through defined date threshold logic
        elif any([thresholds, self.accept_before_date_threshold is False, self.accept_above_date_threshold is False]):
            errors = self._date_threshold(thresholds, date, errors, error_dict, error_string_start)

        return errors

    def gds_validation_on_invalid_date_string(self, value):

        error_dict = {'day': '', 'month': '', 'year': ''}
        errors = ['', error_dict]

        year, month, day = value.split('-')

        day = self.converted_date_str(day, 'day')
        month = self.converted_date_str(month, 'month')
        year = self.converted_date_str(year, 'year')

        _is_blank_list = [day['is_blank_string'], month['is_blank_string'], year['is_blank_string']]

        _is_wrong_format_list = [
            day['is_wrong_format_string'],
            month['is_wrong_format_string'],
            year['is_wrong_format_string'],
        ]

        # Handle blank field logic
        if any([True for date_type in _is_blank_list if date_type != '']):
            error_string_start = f'{self.name} must include a'
            error_string_end = ' and '.join(filter(None, _is_blank_list))
            error_dict.update(
                {
                    'day': self.subwidget_error_class if day['is_blank_string'] else '',
                    'month': self.subwidget_error_class if month['is_blank_string'] else '',
                    'year': self.subwidget_error_class if year['is_blank_string'] else '',
                }
            )

            if year['is_blank_string'] and day['is_blank_string'] == '' and month['is_blank_string'] == '':
                error_string = 'Year must include 4 numbers.'
            else:
                error_string = f'{error_string_start} {error_string_end}.'
            errors = [error_string, error_dict]

        # Handle wrong format logic
        elif any(_is_wrong_format_list):
            error_dict.update(
                {
                    'day': self.subwidget_error_class if day['is_wrong_format_string'] else '',
                    'month': self.subwidget_error_class if month['is_wrong_format_string'] else '',
                    'year': self.subwidget_error_class if year['is_wrong_format_string'] else '',
                }
            )
            errors = [f'{self.name} must be a real date.', error_dict]
        return errors

    def clean(self, value):
        """
        Run the bespoke day, month & year validation
        """
        if value:
            try:
                date_obj = datetime.datetime.strptime(value, '%d/%m/%Y')
                day, month, year = date_obj.strftime('%d/%m/%Y').split('/')
                if len(year) != 4:
                    errors = self.gds_validation_on_invalid_date_string(f'{year}-{month}-{day}')
                else:
                    errors = self.gds_validation_on_valid_date_string(value)
            except (ValueError, TypeError):
                errors = self.gds_validation_on_invalid_date_string(value)
            if errors[0]:
                raise ValidationError(errors[0])
        elif self.required and value is None:
            errors = f'{self.name} must be a real date.'
            raise ValidationError(errors)

        return super().clean(value)