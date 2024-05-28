from django.forms import widgets


class PasswordInputShowHide(widgets.Input):
    input_type = 'password'
    template_name = 'components/great/password-show-hide.html'

    def __init__(self, attrs=None, render_value=False):
        super().__init__(attrs)
        self.render_value = render_value

    def get_context(self, name, value, attrs):
        if not self.render_value:
            value = None
        return super().get_context(name, value, attrs)
