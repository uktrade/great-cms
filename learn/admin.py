from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import LessonPage


class LessonPageAdmin(ModelAdmin):
    model = LessonPage
    list_display = ('title', 'order')


modeladmin_register(LessonPageAdmin)
