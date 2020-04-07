from core.context import AbstractPageContextProvider

from learn import models


class TopicPageContextProvider(AbstractPageContextProvider):

    template_name = 'learn/detail.html'

    @staticmethod
    def get_context_data(request, page):
        queryset = models.LessonViewHit.objects.filter(topic=page, sso_id=request.user.pk)
        return {
            'is_read_collection': queryset.values_list('lesson__pk', flat=True)
        }


class LessonPageContextProvider(AbstractPageContextProvider):

    template_name = 'learn/detail.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'is_read': page.read_hits.filter(sso_id=request.user.pk).exists()
        }
