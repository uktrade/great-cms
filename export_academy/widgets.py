from django.forms import widgets


class GreatRadioSelectWithOtherText(widgets.ChoiceWidget):
    template_name = 'components/great/radios-with-other.html'
    option_template_name = 'components/great/radio-option.html'
    input_type = 'radio'
