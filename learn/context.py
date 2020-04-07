from core.context import AbstractPageContextProvider


class TopicPageContextProvider(AbstractPageContextProvider):

    template_name = 'learn/detail.html'


class LessonPageContextProvider(AbstractPageContextProvider):

    template_name = 'learn/detail.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'is_read': page.read_hits.filter(sso_id=request.user.pk).exists()
        }
