from django.contrib import admin

from core import models


@admin.register(models.PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'sso_id', 'list_page')
    list_filter = ('page', 'sso_id', 'list_page')
