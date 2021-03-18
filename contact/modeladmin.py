from wagtail.contrib.modeladmin.options import ModelAdmin

from .models import ContactSuccessSnippet


class ContactSuccessSnippetAdmin(ModelAdmin):
    model = ContactSuccessSnippet
    exclude_from_explorer = False
    menu_icon = 'fa-check'
    list_display = [
        'internal_title',
    ]


# registered via cms_extras.modeladmin
