from django.forms import widgets
from django import forms
from django.utils.text import slugify


__all__ = [
    'CheckboxSelectInlineLabelMultiple',
    'CheckboxWithInlineLabel',
    'ChoiceWidget',
    'PrettyIDsMixin',
    'RadioSelect',
    'SelectMultipleAutocomplete',
    'TextInputWithSubmitButton',
    'SearchWidget',
]


class PrettyIDsMixin:
    def __init__(self, use_nice_ids=False, *args, **kwargs):
        self.use_nice_ids = use_nice_ids
        self.id_separator = '_'
        if use_nice_ids:
            self.add_id_index = False
            self.id_separator = '-'
        super().__init__(*args, **kwargs)

    def create_option(
            self, name, value, label, selected, index,
            subindex=None, attrs=None):
        """Patch to use nicer ids."""
        index = str(index) if subindex is None else "%s%s%s" % (
            index, self.id_separator, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(
            self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            if self.use_nice_ids:
                option_attrs['id'] = "%s%s%s" % (
                    option_attrs['id'],
                    self.id_separator,
                    slugify(label.lower())
                )
            else:
                option_attrs['id'] = self.id_for_label(
                    option_attrs['id'], index)
        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
            'wrap_label': True,
        }


class SearchWidget(forms.widgets.TextInput):
    hidden_label = ''

    def __init__(self, hidden_label='', *args, **kwargs):

        self.hidden_label = hidden_label
        super().__init__(*args, **kwargs)


class ChoiceWidget(PrettyIDsMixin, widgets.ChoiceWidget):
    pass


class RadioSelect(ChoiceWidget):
    template_name = 'directory_components/form_widgets/multiple_input.html'
    option_template_name = 'directory_components/form_widgets/radio_option.html'
    css_class_name = 'select-multiple'
    input_type = 'radio'
    is_grouped = True


class CheckboxWithInlineLabel(forms.widgets.CheckboxInput):
    template_name = 'directory_components/form_widgets/checkbox_inline.html'

    def __init__(self, label='', help_text=None, *args, **kwargs):
        self.label = label
        self.help_text = help_text
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['label'] = self.label
        context['help_text'] = self.help_text
        return context


class CheckboxSelectInlineLabelMultiple(PrettyIDsMixin, widgets.CheckboxSelectMultiple):
    template_name = 'directory_components/form_widgets/multiple_input.html'
    option_template_name = 'directory_components/form_widgets/checkbox_inline_multiple.html'
    css_class_name = 'select-multiple'
    input_type = 'checkbox'
    is_grouped = True

    def __init__(self, attrs=None, use_nice_ids=False):
        super().__init__(attrs=attrs, use_nice_ids=use_nice_ids)
        self.attrs['class'] = self.attrs.get('class', self.css_class_name)


class SelectMultipleAutocomplete(widgets.SelectMultiple):

    container_css_classes = 'multi-select-autocomplete'

    class Media:
        css = {
            'all': ('directory_components/js/vendor/accessible-autocomplete.min.css',)
        }
        js = (
            'directory_components/js/vendor/accessible-autocomplete.min.js',
            'directory_components/js/dit.components.multiselect-autocomplete.js',
        )


class RadioNestedWidget(RadioSelect):
    option_template_name = 'directory_components/form_widgets/nested-radio.html'
    container_css_classes = 'form-group radio-nested-container'
    is_grouped = True

    def create_option(self, *args, **kwargs):
        return {
            **super().create_option(*args, **kwargs),
            'nested_form': self.nested_form,
            'nested_form_choice': self.nested_form_choice,
        }

    def bind_nested_form(self, form):
        self.nested_form = form


class TextInputWithSubmitButton(forms.TextInput):
    container_css_classes = 'text-input-with-submit-button-container'
    template_name = 'directory_components/form_widgets/text-input-with-submit-button.html'
