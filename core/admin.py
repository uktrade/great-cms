from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wagtail.images.views.images import (
    CreateView as ImageAddView,
    EditView as ImageEditView,
)
from wagtail_modeladmin import views
from wagtail_modeladmin.mixins import ThumbnailMixin
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from core import models


@admin.register(models.PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'sso_id', 'list_page')
    list_filter = ('page', 'sso_id', 'list_page')


class StandardImageEditViewWrapper(views.EditView):
    def get(self, request):
        view = ImageEditView.as_view()
        response = view(request, self.instance_pk)  # pragma: no cover
        return response  # pragma: no cover


class StandardImageCreateViewWrapper(views.CreateView):
    def get(self, request):
        view = ImageAddView.as_view()
        response = view(request)  # pragma: no cover
        return response  # pragma: no cover


@modeladmin_register
class ImageAdmin(ModelAdmin, ThumbnailMixin):
    model = models.AltTextImage
    menu_label = 'Images List'
    menu_order = 300
    menu_icon = 'image'
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        'title',
        'alt_text',
        'size',
    )

    edit_view_class = StandardImageEditViewWrapper
    create_view_class = StandardImageCreateViewWrapper

    def size(self, obj):
        image_size = (
            f'{round(obj.file_size / 1024)}KB' if obj.file_size < 1048000 else f'{round(obj.file_size / 1048000)}MB'
        )
        return image_size

    size.short_description = 'Size'
    size.admin_order_field = 'file_size'


# Disable autocomplete for user creation and password reset forms.
UserAdmin.add_form.base_fields['password1'].widget.attrs['autocomplete'] = 'off'
UserAdmin.add_form.base_fields['password2'].widget.attrs['autocomplete'] = 'off'
UserAdmin.change_password_form.base_fields['password1'].widget.attrs['autocomplete'] = 'off'
UserAdmin.change_password_form.base_fields['password2'].widget.attrs['autocomplete'] = 'off'
