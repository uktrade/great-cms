from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from learn import models


class LessonPageAdmin(ModelAdmin):
    list_display = ('title', 'order')
    model = models.LessonPage


modeladmin_register(LessonPageAdmin)
