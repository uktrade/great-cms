from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from django.contrib import admin

from learn import models


class LessonPageAdmin(ModelAdmin):
    list_display = ('title', 'order')
    model = models.LessonPage


@admin.register(models.LessonViewHit)
class LessonViewHitAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'sso_id',)
    list_filter = ('lesson', 'sso_id',)


modeladmin_register(LessonPageAdmin)
