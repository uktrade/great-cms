from django import forms

from wagtail.utils.widgets import WidgetWithScript


class MarkdownTextarea(WidgetWithScript, forms.widgets.Textarea):
    def __init__(self, **kwargs):
        super(MarkdownTextarea, self).__init__(**kwargs)

    def render_js_init(self, id_, name, value):
        return 'simplemdeAttach("{0}");'.format(id_)

    @property
    def media(self):
        return forms.Media(
            css={'all': ('https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css',)},  # NOQA
            js=(
                'https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js',
                'core/js/refresh_codemirror.js',
                'wagtailadmin/js/page-chooser-modal.js',
            ),
        )
