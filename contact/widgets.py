from django.forms import widgets


class GreatRadioSelect(widgets.ChoiceWidget):
    template_name = 'components/great/radios.html'
    option_template_name = 'components/great/radio-option.html'
    input_type = 'radio'


class GreatCheckboxes(widgets.ChoiceWidget):
    template_name = 'components/great/checkboxes.html'
    option_template_name = 'components/great/checkbox-option.html'
    input_type = 'checkbox'
