from django.contrib import admin
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from wagtail.contrib.modeladmin import views
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.images.views.images import add as image_add_view, edit as image_edit_view

from core import models


@admin.register(models.PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'sso_id', 'list_page')
    list_filter = ('page', 'sso_id', 'list_page')


class StandardImageEditViewWrapper(views.EditView):
    def get(self, request):
        response = image_edit_view(request, self.instance_pk)
        return response


class StandardImageCreateViewWrapper(views.CreateView):
    def get(self, request):
        response = image_add_view(request)
        return response


@modeladmin_register
class ImageAdmin(ModelAdmin, ThumbnailMixin):
    model = models.AltTextImage
    menu_label = "Images List"
    menu_order = 300
    menu_icon = 'image'
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('admin_thumb', 'title', 'file_size', 'alt_text')

    def admin_thumb(self, obj):
        # hacked version of ThumbnailMixin.admin_thumb but image=obj
        img_attrs = {
            'src': self.thumb_default,
            'width': self.thumb_image_width,
            'class': self.thumb_classname,
        }
        # try to get a rendition of the image to use
        from wagtail.images.shortcuts import get_rendition_or_not_found

        spec = self.thumb_image_filter_spec
        rendition = get_rendition_or_not_found(obj, spec)
        img_attrs.update({'src': rendition.url})
        return mark_safe('<img{}>'.format(flatatt(img_attrs)))

    edit_view_class = StandardImageEditViewWrapper
    create_view_class = StandardImageCreateViewWrapper
