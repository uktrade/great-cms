from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import ExportAcademyHomePage


@register(ExportAcademyHomePage)
class ExportAcademyHomePageTO(TranslationOptions):
    fields = ()
