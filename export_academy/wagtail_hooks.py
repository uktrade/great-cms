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
    list_display = ('name', 'start_date', 'link')
    list_filter = ('start_date',)
    search_fields = ('name', 'description')


modeladmin_register(EventsAdmin)
