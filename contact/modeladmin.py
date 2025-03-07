from wagtail_modeladmin.options import ModelAdmin

from .models import ContactSuccessSnippet, ContactUsGuidanceSnippet

# All of these are registered via cms_extras.modeladmin


class ContactSuccessSnippetAdmin(ModelAdmin):
    model = ContactSuccessSnippet
    exclude_from_explorer = False
    menu_icon = 'check'
    list_display = [
        'internal_title',
    ]
    menu_label = 'Contact Success Page content'


class ContactUsGuidanceSnippetAdmin(ModelAdmin):
    model = ContactUsGuidanceSnippet
    exclude_from_explorer = False
    menu_icon = 'check'
    list_display = [
        'internal_title',
    ]
    menu_label = 'Contact Us Guidance content'


# All of these are registered via cms_extras.modeladmin
