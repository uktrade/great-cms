from django.contrib.admin.utils import quote
from django.urls import re_path
from django.utils.translation import gettext_lazy
from wagtail_modeladmin.helpers import ButtonHelper
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_modeladmin.views import CreateView, InstanceSpecificView

from export_academy.models import Event


class CloneView(CreateView, InstanceSpecificView):
    page_title = gettext_lazy('Cloning')


class EventAdminButtonHelper(ButtonHelper):
    """EventAdminButtonHelper handles special button configuration for Events on Wagtail admin."""

    clone_button_classnames = ['button-small', 'button-secondary']

    def clone_button(self, obj):
        classname = self.finalise_classname(classnames_add=self.clone_button_classnames)

        return {
            'url': self.url_helper.get_action_url('clone', quote(obj.pk)),
            'label': gettext_lazy('Clone'),
            'classname': classname,
            'title': gettext_lazy('Clone a new %s') % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        if 'clone' not in (exclude or []):
            btns.insert(1, self.clone_button(obj))

        return btns


class EventAdmin(ModelAdmin):
    """EventAdmin allows to add the Event model to the Wagtail admin."""

    model = Event
    button_helper_class = EventAdminButtonHelper
    clone_view_class = CloneView
    base_url_path = 'events'
    menu_label = 'Events'
    menu_icon = 'date'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    add_to_admin_menu = True
    list_display = ('name', 'get_types', 'start_date', 'get_status')
    list_filter = ('start_date', 'types')
    search_fields = ('name', 'description')

    def get_types(self, obj):
        return ', '.join(str(type.name) for type in obj.types.all())

    get_types.short_description = 'Type'

    def get_status(self, obj):
        return 'LIVE' if obj.live else 'DRAFT'

    get_status.short_description = 'Status'

    def clone_view(self, request, **kwargs):
        kwargs.update(**{'model_admin': self})
        view_class = self.clone_view_class

        return view_class.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        urls += (
            re_path(
                self.url_helper.get_action_url_pattern('clone'),
                self.clone_view,
                name=self.url_helper.get_action_url_name('clone'),
            ),
        )

        return urls


modeladmin_register(EventAdmin)
