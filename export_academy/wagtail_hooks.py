from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from export_academy import models


class EventsAdmin(ModelAdmin):
    model = models.Event
    base_url_path = 'events'
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    add_to_admin_menu = True
    list_display = ('name', 'get_types', 'start_date')
    list_filter = ('start_date', 'types')
    search_fields = ('name', 'description')

    def get_types(self, obj):
        return ', '.join(str(type.name) for type in obj.types.all())

    get_types.short_description = 'Type'


modeladmin_register(EventsAdmin)
