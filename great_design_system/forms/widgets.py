from captcha.widgets import ReCaptchaV3
from django.forms import widgets
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

    def __init__(self, fieldset=False, linked_conditional_reveal_fields=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldset = fieldset
        self.linked_conditional_reveal_fields = linked_conditional_reveal_fields

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        field = self.field
        linked_conditional_reveal_fields = (
            self.linked_conditional_reveal_fields if hasattr(self, 'linked_conditional_reveal_fields') else []
        )
        ctx['field'] = field
        ctx['linked_conditional_reveal_fields'] = linked_conditional_reveal_fields
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

    def get_option_help_text(self, value):

        help_dict = {'help_text': '', 'help_text_css': ''}
        if hasattr(self, 'choice_help_text'):
            for help_text_choice_name, help_text_choice_text in self.choice_help_text:
                if value == help_text_choice_name:
                    help_dict.update({'help_text': help_text_choice_text, 'help_text_css': self.help_text_class_name})
        return help_dict

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
            'template_name': self.option_template_name,
            'wrap_label': True,
            'reveals': self.get_option_reveal_fields(value),
        }

        options.update(**self.get_option_help_text(value))
        return options


class ChoiceWidget(CreateOptionMixin, ChoiceWidget):
    pass


class RadioSelect(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    template_name = '_multiple_input.html'
    option_template_name = '_radio_option.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True
    help_text_class_name = 'govuk-radios__hint'


class RadioSelectConditionalReveal(ChoiceWidget):
    """
    New widget that will play nicely with the great-design-system
    """

    template_name = '_multiple_input.html'
    option_template_name = '_radio_option_conditional_reveal.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True
    help_text_class_name = 'govuk-radios__hint'


class Textarea(Textarea):
    """
    New widget that will play nicely with the great-design-system
    """

    input_type = 'text'
    template_name = '_textarea.html'


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


class ReCaptchaV3(ReCaptchaV3, HiddenInput):
    pass
