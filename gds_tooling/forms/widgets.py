from captcha.widgets import ReCaptchaV3
from django.forms import widgets
from django.utils.text import slugify


def create_optional_reveal_widget(name, classes='', label=''):
    optgroup = {
        'name': name,
        'label': label,
        'attrs': {'class': classes},
        'type': 'text',
        'id': f'id_{name}'
    }
    return optgroup
class WidgetGDSMixin(widgets.Widget):
    '''
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
            'gds_mapping':{
                'label': {
                    'class': '',
                    'text': 'Text area example',
                    'id': '1234-5678-9101-1121'
                },
                'hint': {
                    'class': '',
                    'text': 'This is a hint',
                    'id': 'id-example'
                },
                'error': {}
            }
        }
    }
    '''

    field = None

    def __init__(self, linked_conditional_reveal_fields = None,fieldset = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldset = fieldset
        self.linked_conditional_reveal_fields = linked_conditional_reveal_fields

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        field = self.field
        ctx['field'] = field

        if hasattr(field, 'hide_on_page_load'):
            if hasattr(ctx["widget"]["attrs"], 'class'):
                widget_class = ctx["widget"]["attrs"]["class"]
                ctx["widget"]["attrs"]["class"] = f'hide-on-page-load {widget_class}'
        return ctx


def widget_factory(base_class):
    bases = (WidgetGDSMixin, base_class)
    return type(base_class.__name__, bases, {})


TextInput = widget_factory(widgets.TextInput)
NumberInput = widget_factory(widgets.NumberInput)
EmailInput = widget_factory(widgets.EmailInput)
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
RadioSelect = widget_factory(widgets.RadioSelect)
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

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        """Patch to use nicer ids."""
        index = str(index) if subindex is None else "%s%s%s" % (index, self.id_separator, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            if self.use_nice_ids:
                option_attrs['id'] = "%s%s%s" % (option_attrs['id'], self.id_separator, slugify(label.lower()))
            else:
                option_attrs['id'] = self.id_for_label(option_attrs['id'], index)
        reveal_fields = []
        if value == 'yes':
            if self.linked_conditional_reveal_fields:
                for reveal_field_name in self.linked_conditional_reveal_fields:
                    reveal_field_name['template_name'] = '_reveal_input.html' 
                    reveal_fields.append(reveal_field_name)
        
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
            'reveals': reveal_fields
        }
        return options


class ChoiceWidget(CreateOptionMixin, ChoiceWidget):
    pass


class GDSChoiceWidget(ChoiceWidget):
    pass

class RadioSelect(ChoiceWidget):
    template_name = 'multiple_input.html'
    option_template_name = 'radio_option.html'
    css_class_name = 'g-select-multiple'
    input_type = 'radio'


class GDSRadioSelect(GDSChoiceWidget):
    '''
    New widget that will play nicely with the great-design-system
    '''

    template_name = '__multiple_input.html'
    option_template_name = '_radio_option.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True


class GDSRadioConditionalRevealSelect(GDSChoiceWidget):
    '''
    New widget that will play nicely with the great-design-system
    '''

    template_name = '_multiple_input.html'
    option_template_name = '_radio_option_conditional_reveal.html'
    option_reveal_template_name = '_reveal_input.html'
    use_fieldset = True


class CheckboxWithInlineLabel(CheckboxInput):
    template_name = 'checkbox_inline.html'
    container_css_classes = 'form-group'

    def __init__(self, label='', help_text=None, *args, **kwargs):
        self.label = label
        self.help_text = help_text
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['label'] = self.label
        context['help_text'] = self.help_text
        return context


class CheckboxSelectInlineLabelMultiple(CreateOptionMixin, CheckboxSelectMultiple):
    template_name = 'multiple_input.html'
    option_template_name = 'checkbox_inline_multiple.html'
    css_class_name = 'g-select-multiple'
    input_type = 'checkbox'

    def __init__(self, attrs=None, use_nice_ids=False):
        super().__init__(attrs=attrs, use_nice_ids=use_nice_ids)
        self.attrs['class'] = self.attrs.get('class', self.css_class_name)


class GDSCheckboxSelectInlineLabelMultiple(CheckboxSelectInlineLabelMultiple):
    template_name = '_multiple_input.html'
    option_template_name = '_checkbox_option.html'


class GDSDjangoCopyTextarea(Textarea):
    '''
    New widget that will play nicely with the great-design-system
    '''

    input_type = 'text'
    template_name = '__textarea.html'


class GDSDjangoCopyTextInput(TextInput):
    '''
    New widget that will play nicely with the great-design-system
    '''

    template_name = '__input.html'


class GDSDjangoCopyEmailInput(GDSDjangoCopyTextInput):
    '''
    New widget that will play nicely with the great-design-system
    '''

    input_type = 'email'


class GDSTextarea(Textarea):
    '''
    New widget that will play nicely with the great-design-system
    '''

    input_type = 'text'
    template_name = '_textarea.html'


class GDSTextInput(TextInput):
    '''
    New widget that will play nicely with the great-design-system
    '''

    template_name = '_input.html'


class GDSEmailInput(GDSTextInput):
    '''
    New widget that will play nicely with the great-design-system
    '''

    input_type = 'email'


class GDSHiddenInput(HiddenInput):
    '''
    New widget that will play nicely with the great-design-system
    '''

    input_type = 'hidden'
    template_name = '_hidden_input.html'

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx["widget"]["type"] = self.input_type
        return ctx


class GDSReCaptchaV3(ReCaptchaV3, GDSHiddenInput):
    pass
