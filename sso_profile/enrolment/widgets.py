import django.forms
import gds_tooling.forms


class PostcodeInput(django.forms.TextInput):
    template_name = 'enrolment/widgets/postcode.html'


class RadioSelect(gds_tooling.forms.RadioSelect):
    option_template_name = 'enrolment/widgets/radio_option.html'

    def __init__(self, help_text, *args, **kwargs):
        self.help_text = help_text
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        option['help_text'] = self.help_text.get(value)
        return option
