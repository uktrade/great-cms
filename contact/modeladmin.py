from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import ContactSuccessSnippet


class ContactSuccessSnippetAdmin(ModelAdmin):
    model = ContactSuccessSnippet
    exclude_from_explorer = False
    menu_icon = 'fa-check'
    list_display = [
        'internal_title',
    ]


class NonCMSContentGroup(ModelAdminGroup):
    menu_label = 'Non-page content'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 200
    items = (ContactSuccessSnippetAdmin,)


modeladmin_register(NonCMSContentGroup)
