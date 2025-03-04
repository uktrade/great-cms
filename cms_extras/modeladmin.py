import csv

from django.utils.html import format_html_join, strip_tags
from wagtail.admin.views.mixins import Echo
from wagtail_modeladmin.helpers import ButtonHelper
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from wagtail_modeladmin.views import IndexView

from contact.modeladmin import ContactSuccessSnippetAdmin, ContactUsGuidanceSnippetAdmin
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


class CaseStudySpreadsheetExportMixin:
    columns_to_convert = [
        'associated_country_code_tags',
        'associated_hs_code_tags',
        'associated_region_code_tags',
        'associated_trading_bloc_code_tags',
        'get_related_pages',
        'modified',
    ]

    def stream_csv(self, queryset):
        """Generate a csv file line by line from queryset, to be used in a StreamingHTTPResponse"""

        writer = csv.DictWriter(
            Echo(),
            fieldnames=[field for field in self.list_export if field not in self.columns_to_convert],
        )
        yield writer.writerow(
            {
                field: self.get_heading(queryset, field)
                for field in self.list_export
                if field not in self.columns_to_convert
            }
        )

        for item in queryset:
            yield self.write_csv_row(writer, self.to_row_dict(item))

    def create_row_by_tag(self, row_dict, processed_row) -> list:
        """
        This is to create number of rows based on how many tag attached to a Case study
        For example, HS code tag field has value like 12,123456 then we convert to two rows in CSV like below
        title, summary_context, lead_title, association, attribute
        <title>, <summary_context>, <lead_title>, associated_hs_tag, 12
        <title>, <summary_context>, <lead_title>, associated_hs_tag, 123456
        """
        processed_row_list = []
        for f in self.columns_to_convert:
            # No tagged value then just append row for write
            attr_values = [] if row_dict.get(f) == '-' else row_dict.get(f)
            if f == 'get_related_pages':
                attr_values = (
                    []
                    if row_dict.get(f) in ['-', None]
                    else ([strip_tags(i) for i in row_dict.get(f).split('<br>') if i])
                )

            if f == 'modified':
                tag = {'attribute': attr_values, 'association': f}
                processed_row_with_tag = dict(processed_row, **tag)
                processed_row_list.append(processed_row_with_tag)
                continue
            elif attr_values:
                for tagged_value in attr_values:
                    tag = {'attribute': tagged_value, 'association': f}
                    processed_row_with_tag = dict(processed_row, **tag)
                    processed_row_list.append(processed_row_with_tag)

        return processed_row_list

    def write_multiple_rows(self, writer, processed_row_list) -> bytes:
        processed_byte_string = b''
        for row in processed_row_list:
            processed_byte_string += writer.writerow(row)
        return processed_byte_string

    def write_csv_row(self, writer, row_dict) -> bytes:
        processed_row = {}
        common_fields = {k: v for k, v in row_dict.items() if k in ['title', 'summary_context', 'lead_title']}
        for field, value in common_fields.items():
            preprocess_function = self.get_preprocess_function(field, value, self.FORMAT_CSV)
            processed_value = preprocess_function(value) if preprocess_function else value
            processed_row[field] = processed_value
        return self.write_multiple_rows(writer, self.create_row_by_tag(row_dict, processed_row))


class CaseStudyIndexView(CaseStudySpreadsheetExportMixin, IndexView):
    pass


class CaseStudyAdmin(ModelAdmin):
    model = CaseStudy
    add_to_settings_menu = False
    button_helper_class = CaseStudyAdminButtonHelper
    exclude_from_explorer = False
    menu_icon = 'book'
    export_filename = 'casestudies-export'
    index_view_class = CaseStudyIndexView

    list_export = [
        'title',
        'summary_context',
        'lead_title',
        'association',
        'attribute',
        'associated_hs_code_tags',
        'associated_country_code_tags',
        'associated_region_code_tags',
        'associated_trading_bloc_code_tags',
        'get_related_pages',
        'modified',
    ]
    list_display = (
        '__str__',
        'associated_hs_code_tags',
        'associated_country_code_tags',
        'associated_region_code_tags',
        'associated_trading_bloc_code_tags',
        'get_related_pages',
        'modified',
    )
    # list_filter = (  # DISABLED BECAUSE SLOWING DOWN THE PAGE TOO MUCH
    #     'hs_code_tags',
    #     'country_code_tags',
    # )
    search_fields = (
        'title',
        'summary_context',
        'lead_title',
        # DISABLED DUE TO SLOWNESS, also it could be cause or UAT DB crash on 21/05/21
        # 'hs_code_tags__name',
        # 'country_code_tags__name',
        # 'region_code_tags__name',
        # 'trading_bloc_code_tags__name',
    )

    def associated_hs_code_tags(self, obj):
        return [str(x) for x in obj.hs_code_tags.all()]

    def associated_country_code_tags(self, obj):
        return [str(x) for x in obj.country_code_tags.all()]

    def associated_region_code_tags(self, obj):
        return [str(x) for x in obj.region_code_tags.all()]

    def associated_trading_bloc_code_tags(self, obj):
        return [str(x) for x in obj.trading_bloc_code_tags.all()]

    def get_related_pages(self, obj):
        page_mapping = {
            'curatedlistpage': 'MODULE',
            'topicpage': 'TOPIC',
            'detailpage': 'LESSON',
        }
        return format_html_join(
            '',
            '<strong>{}: </strong> {}<br>',  # noqa
            ((page_mapping.get(x.page.specific._meta.model_name), x.page) for x in obj.related_pages.all() if x.page),
        )

    get_related_pages.short_description = 'Associated pages'

    def association(self, obj):
        # This is used in list_export field for CSV download
        # when define in list_export it verify actual attribute exist for model or not hence creating proxy field here
        pass

    def attribute(self, obj):
        # This is used in list_export field for CSV download
        # when define in list_export it verify actual attribute exist for model or not hence creating proxy field here
        pass


modeladmin_register(CaseStudyAdmin)


class NonCMSContentGroup(ModelAdminGroup):
    """All of the snippets used for hybrid-content pages
    should be registered as part of this group"""

    menu_label = 'Non-page content'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 200
    items = (
        ContactSuccessSnippetAdmin,
        ContactUsGuidanceSnippetAdmin,
        # Add more here
    )


modeladmin_register(NonCMSContentGroup)
