from django.forms import widgets


class GreatRadioSelect(widgets.ChoiceWidget):
    template_name = 'components/great/radios.html'
    option_template_name = 'components/great/radio-option.html'
    input_type = 'radio'
