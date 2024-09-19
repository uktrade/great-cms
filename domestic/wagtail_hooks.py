from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks

# from wagtail.admin.panels import ObjectList, TabbedInterface

# from domestic.models import ArticlePage


@hooks.register('insert_editor_css')
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',  # noqa: P103
        static('cms-admin/css/domestic-editor.css'),
    )


@hooks.register('insert_global_admin_css')
def global_admin_css():
    env_stylesheet = ''

    if getattr(settings, 'ENVIRONMENT_CSS_THEME_FILE'):
        env_stylesheet = format_html(
            '<link rel="stylesheet" href="{}">',  # noqa: P103
            static(settings.ENVIRONMENT_CSS_THEME_FILE),
        )

    return (
        format_html(
            '<link rel="stylesheet" href="{}">',  # noqa: P103
            static('cms-admin/css/domestic.css'),
        )
    ) + env_stylesheet


# @hooks.register('before_edit_page')
# def modify_panels(request, page):
#     print(f'Before edit page {page}')
#     if isinstance(page, ArticlePage):
#         print('Instance of Article Page')
#         edit_handler = page.get_edit_handler()
#         print(f'Primark key {page.pk}')
#         tagging_panels = ObjectList(ArticlePage.tagging_panels, heading='Tags').bind_to_model(ArticlePage)
#         panels = edit_handler.children
#         print(f'PANELS : {panels}')
#         panels.insert(1, tagging_panels)
#         # panels.append(tagging_panels)
#         print(f'AFTER APPEND PANELS : {panels}')
#         return TabbedInterface(panels).bind_to_model(ArticlePage)
