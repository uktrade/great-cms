from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from core.models import CaseStudy


class CaseStudyAdminButtonHelper(ButtonHelper):

    view_button_classnames = ['button-small', 'icon', 'icon-doc']

    def view_button(self, obj):
        """Button to trigger a standalone view of the relevant CaseStudy"""
        text = f'View {self.verbose_name}'
        return {
            'classname': self.finalise_classname(self.view_button_classnames),
            'label': text,
            'title': text,
            'url': obj.get_cms_standalone_view_url(),
        }

    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        if 'view' not in (exclude or []):
            btns.append(self.view_button(obj))
        return btns


class CaseStudyAdmin(ModelAdmin):
    model = CaseStudy
    add_to_settings_menu = False
    button_helper_class = CaseStudyAdminButtonHelper
    exclude_from_explorer = False
    menu_icon = 'fa-book'
    list_display = ('__str__', 'associated_hs_code_tags', 'associated_country_code_tags')
    # list_filter = (  # DISABLED BECAUSE SLOWING DOWN THE PAGE TOO MUCH
    #     'hs_code_tags',
    #     'country_code_tags',
    # )
    search_fields = (
        'title',
        'company_name',
        'country_code_tags__name',
        'hs_code_tags__name',
    )

    def associated_hs_code_tags(self, obj):
        return [str(x) for x in obj.hs_code_tags.all()]

    def associated_country_code_tags(self, obj):
        return [str(x) for x in obj.country_code_tags.all()]


modeladmin_register(CaseStudyAdmin)
