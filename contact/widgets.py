from django.forms import widgets

from gds_tooling import forms


class GreatRadioSelect(widgets.ChoiceWidget):
    template_name = 'components/great/radios.html'
    option_template_name = 'components/great/radio-option.html'
    input_type = 'radio'


class GreatFilteredRadioSelect(widgets.ChoiceWidget):
    template_name = 'components/great/filtered-radios.html'
    option_template_name = 'components/great/radio-option.html'
    input_type = 'radio'


class GreatCheckboxes(forms.CheckboxSelectInlineLabelMultiple):
    template_name = 'components/great/checkboxes.html'
    option_template_name = 'components/great/checkbox-option.html'
    input_type = 'checkbox'
