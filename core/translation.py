from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from .models import (
    CuratedListPage,
    LandingPage,
    LessonPlaceholderPage,
    ListPage,
    Microsite,
    MicrositePage,
    TopicPage,
)


@register(MicrositePage)
class MicrositePageTranslationOptions(TranslationOptions):
    fields = (
        'page_title',
        'page_subheading',
        'page_teaser',
        'hero_image',
        'hero_video',
        'hero_video_transcript',
        'page_body',
        'cta_title',
        'cta_teaser',
        'cta_link_label',
        'related_links',
    )


@register(Microsite)
class MicrositeTO(TranslationOptions):
    fields = ()


@register(LandingPage)
class LandingPageTO(TranslationOptions):
    fields = ()


@register(ListPage)
class ListPageTO(TranslationOptions):
    fields = ()


@register(CuratedListPage)
class CuratedListPageTO(TranslationOptions):
    fields = ()


@register(TopicPage)
class TopicPageTO(TranslationOptions):
    fields = ()


@register(LessonPlaceholderPage)
class LessonPlaceholderPageTO(TranslationOptions):
    fields = ()
