from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import IOOArticlePage, IOOGuidePage, IOOIndexPage


@register(IOOIndexPage)
class IOOIndexPageTO(TranslationOptions):
    fields = ()


@register(IOOGuidePage)
class IOOGuidePageTO(TranslationOptions):
    fields = ()


@register(IOOArticlePage)
class IOOArticlePageTO(TranslationOptions):
    fields = ()
