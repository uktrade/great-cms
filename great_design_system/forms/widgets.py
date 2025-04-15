import datetime

from captcha.widgets import ReCaptchaV3
from django.forms import widgets
from django.utils import formats
from django.utils.formats import get_format
from django.utils.text import slugify


class GDSWidgetMixin(widgets.Widget):
    """
    Used to add field to widget context.

    context = {
        'widget': {
            'name': 'example',
            'value': 'Example value',
            'id_for_label': 'id-example',
            'attrs': {
                'rows': 5
            }
        },
        'field': {
            ...
        }
    }
    """

    field = None
    help_text_class_name = ''

    def __init__(
        self,
        container_css_classes='',
        data_module_attrs={},
        fieldset=False,
        linked_conditional_reveal_fields=[],
        choices=[],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fieldset = fieldset
        self.linked_conditional_reveal_fields = linked_conditional_reveal_fields
        self.data_module_attrs = data_module_attrs
        self.container_css_classes = container_css_classes
        self.choices = choices

    def get_context(self, name, value, attrs, subwidget_label=''):
        ctx = super().get_context(name, value, attrs)
        field = self.field
        linked_conditional_reveal_fields = (
            self.linked_conditional_reveal_fields if hasattr(self, 'linked_conditional_reveal_fields') else []
        )
        ctx['field'] = field
        ctx['linked_conditional_reveal_fields'] = linked_conditional_reveal_fields
        ctx['subwidget_label'] = subwidget_label
        return ctx


def widget_factory(base_class):
    bases = (GDSWidgetMixin, base_class)
    return type(base_class.__name__, bases, {})


TextInput = widget_factory(widgets.TextInput)
NumberInput = widget_factory(widgets.NumberInput)
URLInput = widget_factory(widgets.URLInput)
PasswordInput = widget_factory(widgets.PasswordInput)
HiddenInput = widget_factory(widgets.HiddenInput)
MultipleHiddenInput = widget_factory(widgets.MultipleHiddenInput)
FileInput = widget_factory(widgets.FileInput)
ClearableFileInput = widget_factory(widgets.ClearableFileInput)
Textarea = widget_factory(widgets.Textarea)
DateInput = widget_factory(widgets.DateInput)
DateTimeInput = widget_factory(widgets.DateTimeInput)
TimeInput = widget_factory(widgets.TimeInput)
CheckboxInput = widget_factory(widgets.CheckboxInput)
NullBooleanSelect = widget_factory(widgets.NullBooleanSelect)
SelectMultiple = widget_factory(widgets.SelectMultiple)
CheckboxSelectMultiple = widget_factory(widgets.CheckboxSelectMultiple)
MultiWidget = widget_factory(widgets.MultiWidget)
SplitDateTimeWidget = widget_factory(widgets.SplitDateTimeWidget)
SplitHiddenDateTimeWidget = widget_factory(widgets.SplitHiddenDateTimeWidget)
SelectDateWidget = widget_factory(widgets.SelectDateWidget)
ChoiceWidget = widget_factory(widgets.ChoiceWidget)
Select = widget_factory(widgets.Select)


class CreateOptionMixin:
    def __init__(self, use_nice_ids=False, *args, **kwargs):
        self.use_nice_ids = use_nice_ids
        self.id_separator = '_'
        if use_nice_ids:
            self.add_id_index = False
            self.id_separator = '-'
        super().__init__(*args, **kwargs)

    def get_option_reveal_fields(self, value):
        reveal_fields = []
        if hasattr(self, 'linked_conditional_reveal_choice'):
            if value == self.linked_conditional_reveal_choice:
                reveal_fields = (
                    self.linked_conditional_reveal_fields if hasattr(self, 'linked_conditional_reveal_fields') else []
                )
        return reveal_fields

    def get_exclusive(self, value):
        if hasattr(self.field, 'exclusive_choice'):
            if value == self.field.exclusive_choice:
                return True
        return False

    def get_option_help_text(self, value):

        help_dict = {'help_text': '', 'help_text_css': ''}
        if hasattr(self, 'choice_help_text'):
            for help_text_choice_name, help_text_choice_text in self.choice_help_text:
                if value == help_text_choice_name:
                    help_dict.update({'help_text': help_text_choice_text, 'help_text_css': self.help_text_class_name})
        return help_dict

    def format_groups(self, option_label, option_value):
        if isinstance(option_label, (list, tuple)):
            group_name = option_value
            subindex = 0
            choices = option_label
        else:
            group_name = None
            subindex = None
            choices = [(option_value, option_label)]
        return group_name, subindex, choices

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        for index, (option_value, *option_label) in enumerate(self.choices):

            # patch to pass through checked options and pass through to optgroup widget attrs
            if len(option_label) > 1:
                if option_label[1]:
                    value = [option_value]

            option_label = option_label[0]

            if option_value is None:
                option_value = ''

            subgroup = []
            group_name, subindex, choices = self.format_groups(option_label, option_value)
            groups.append((group_name, subgroup, index))
            for subvalue, sublabel in choices:
                selected = (not has_selected or self.allow_multiple_selected) and str(subvalue) in value
                has_selected |= selected
                subgroup.append(
                    self.create_option(name, subvalue, sublabel, selected, index, subindex=subindex, attrs=attrs)
                )
                if subindex is not None:
                    subindex += 1
        return groups

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        """Patch to use nicer ids and add conditional reveal fields to ChoiceFields."""
        index = str(index) if subindex is None else '%s%s%s' % (index, self.id_separator, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            if self.use_nice_ids:
                option_attrs['id'] = '%s%s%s' % (option_attrs['id'], self.id_separator, slugify(label.lower()))
            else:
                option_attrs['id'] = self.id_for_label(option_attrs['id'], index)

        options = {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_class_name': self.template_class_name,
            'template_name': self.option_template_name,
            'wrap_label': True,
            'reveals': self.get_option_reveal_fields(value),
            'exclusive': self.get_exclusive(value),
        }

        options.update(**self.get_option_help_text(value))
        return options


class ChoiceWidget(CreateOptionMixin, ChoiceWidget):
    pass


class RadioSelect(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'radio'
    template_class_name = 'radios'
    template_name = '_multiple_input.html'
    option_template_name = '_option.html'
    use_fieldset = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        return context


class RadioSelectConditionalReveal(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'radio'
    template_class_name = 'radios'
    template_name = '_multiple_input.html'
    option_template_name = '_option_conditional_reveal.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        return context


class SelectOne(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    template_name = '_select.html'
    option_template_name = '_select_option.html'
    template_class_name = 'select'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        return context


class Textarea(Textarea):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'text'
    template_name = '_textarea.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        field = context['field']
        context['widget'].update(
            {
                'counter': field.counter,
                'max_length': field.max_length,
                'max_length_info': f'You can enter up to  {field.max_length} characters',
                'max_words': field.max_words,
                'max_words_info': f'You can enter up to  {field.max_words} words',
            }
        )
        return context


class TextInput(TextInput):
    """
    New widget that will play nicely with the great-design-system
    """

    template_name = '_input.html'


class EmailInput(TextInput):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'email'


class HiddenInput(HiddenInput):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'hidden'
    template_name = '_hidden_input.html'

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx['widget']['type'] = self.input_type
        return ctx


class PasswordInput(PasswordInput):

    input_type = 'password'
    template_name = '_password-input.html'


class CheckboxSelectMultiple(ChoiceWidget, CheckboxSelectMultiple):

    input_type = 'checkbox'
    template_class_name = 'checkboxes'
    template_name = '_multiple_input.html'
    option_template_name = '_option.html'
    use_fieldset = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        return context


class CheckboxSelectConditionalReveal(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'checkbox'
    template_class_name = 'checkboxes'
    template_name = '_multiple_input.html'
    option_template_name = '_option_conditional_reveal.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        return context


class CheckboxSelectMultipleSmall(CheckboxSelectMultiple):

    input_type = 'checkbox'
    template_class_name = 'checkboxes'
    is_small = True
    template_name = '_multiple_input.html'
    option_template_name = '_option.html'
    use_fieldset = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['template_class_name'] = self.template_class_name
        context['widget']['is_small'] = self.is_small
        return context


class TypeDateWidget(SelectDateWidget):

    template_name = '_date_input.html'
    input_type = 'text'
    date_widget = TextInput

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        base_attrs = context['widget']['attrs']
        base_attrs.update({'class': 'govuk-input govuk-input--width-4'})
        date_context = {}
        year_name = self.year_field % name
        date_context['year'] = self.date_widget(attrs).get_context(
            name=year_name,
            value=context['widget']['value']['year'],
            attrs={**base_attrs, 'id': 'id_%s' % year_name},
        )
        base_attrs.update({'class': 'govuk-input govuk-input--width-2'})
        month_name = self.month_field % name
        date_context['month'] = self.date_widget(attrs).get_context(
            name=month_name,
            value=context['widget']['value']['month'],
            attrs={**context['widget']['attrs'], 'id': 'id_%s' % month_name},
        )
        day_name = self.day_field % name
        date_context['day'] = self.date_widget(
            attrs,
        ).get_context(
            name=day_name,
            value=context['widget']['value']['day'],
            attrs={**context['widget']['attrs'], 'id': 'id_%s' % day_name},
        )
        subwidgets = []
        for field in self._parse_date_fmt():
            subwidgets.append([date_context[field]['widget'], field.title])
        context['widget']['subwidgets'] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == '':
            return None
        if y is not None and m is not None and d is not None:
            input_format = get_format('DATE_INPUT_FORMATS')[0]
            input_format = formats.sanitize_strftime_format(input_format)
            try:
                date_value = datetime.date(int(y), int(m), int(d))
            except ValueError:
                # Return pseudo-ISO dates with zeros for any unselected values,
                # e.g. '2017-0-23'.
                return '%s-%s-%s' % (y or 0, m or 0, d or 0)
            except OverflowError:
                return '0-0-0'
            return date_value.strftime(input_format)
        return data.get(name)


class ReCaptchaV3(ReCaptchaV3, HiddenInput):
    pass
