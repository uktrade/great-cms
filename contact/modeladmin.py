from wagtail.contrib.modeladmin.options import ModelAdmin

from .models import ContactPageContentSnippet, ContactSuccessSnippet

# All of these are registered via cms_extras.modeladmin


class ContactPageContentSnippetAdmin(ModelAdmin):
    model = ContactPageContentSnippet
    exclude_from_explorer = False
    menu_icon = 'fa-check'
    list_display = [
        'internal_title',
    ]
    menu_label = 'Contact Form Page content'


class ContactSuccessSnippetAdmin(ModelAdmin):
    model = ContactSuccessSnippet
    exclude_from_explorer = False
    menu_icon = 'fa-check'
    list_display = [
        'internal_title',
    ]
    menu_label = 'Contact Success Page content'


# All of these are registered via cms_extras.modeladmin
