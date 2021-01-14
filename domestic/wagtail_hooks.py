from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from wagtail.core import hooks


@hooks.register('insert_editor_css')
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',  # noqa: P103
        static('cms-admin/css/domestic-editor.css'),
    )


@hooks.register('insert_global_admin_css')
def global_admin_css():
    env_stylesheet = ''

    if hasattr(settings, 'ENVIRONMENT_CSS_THEME_FILE'):
        env_stylesheet = format_html(
            '<link rel="stylesheet" href="{}">',  # noqa: P103
            static(settings.ENVIRONMENT_CSS_THEME_FILE),
        )

    return (
        format_html(
            '<link rel="stylesheet" href="{}">',  # noqa: P103
            static('cms-admin/css/domestic-editor.css'),
        )
    ) + env_stylesheet
