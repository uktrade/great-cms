from django.contrib import admin
from django.forms.utils import flatatt
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from wagtail.contrib.modeladmin import views
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.images.views.images import edit as image_edit_view

from core import models


@admin.register(models.PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'sso_id', 'list_page')
    list_filter = ('page', 'sso_id', 'list_page')


class StandardImageEditViewWrapper(views.EditView):
    def get(self, request):
        response = image_edit_view(request, self.instance_pk)
        # hack the normal form post url so we can get redirected back to this view
        standard_post_url = reverse('wagtailimages:edit', args=[self.instance_pk])
        print("HAHAHA:", standard_post_url)
        print(response.content)
        # response.content = response.content.decode('utf8').replace(
        #     standard_post_url, self.edit_url
        # ).encode('utf8')
        return response

    def post(self, request):
        response = image_edit_view(request, self.instance_pk)
        if response.status_code == 302:
            # intercept redirects that would go back to normal image edit
            # and bring them back here
            return redirect(self.get_success_url())


@modeladmin_register
class ImageAdmin(ModelAdmin, ThumbnailMixin):
    model = models.AltTextImage
    menu_label = "CustomImages"
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('admin_thumb', 'title', 'file', "file_size", "alt_text")

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
