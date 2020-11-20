from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register
)

from core.models import CaseStudy


class CaseStudyAdmin(ModelAdmin):
    model = CaseStudy
    add_to_settings_menu = False
    exclude_from_explorer = False
    menu_icon = 'fa-book'
    list_display = (
        '__str__',
        'associated_hs_code_tags',
        'associated_country_code_tags'
    )
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
