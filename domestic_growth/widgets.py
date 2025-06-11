from django.forms import widgets


class SelectOneButton(widgets.Select):
    """
    Select widget styled as multiple ds buttons with selected state
    """

    template_name = 'components/great/select-buttons.html'
    template_class_name = 'select'

    def __init__(
        self,
        name='',
        choices=[],
        buttons_container_classes='',
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.choices = choices
        self.name = name
        self.buttons_container_classes = buttons_container_classes

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['choices'] = self.choices
        context['name'] = self.name
        context['buttons_container_classes'] = self.buttons_container_classes

        return context
