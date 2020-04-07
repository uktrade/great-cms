# from core.context import AbstractPageContextProvider
#
# from learn import models
#
#
# class TopicPageContextProvider(AbstractPageContextProvider):
#
#     template_name = 'learn/detail.html'
#
#     @staticmethod
#     def get_context(request):
#         queryset = models.LessonViewHit.objects.filter(topic=self, sso_id=request.user.pk)
#         return {
#             'is_read_collection': queryset.values_list('lesson__pk', flat=True)
#         }
#
#
# class LessonPageContextProvider(AbstractPageContextProvider):
#
#     template_name = 'learn/detail.html'
#
#     @staticmethod
#     def get_context(request):
#         return {
#             'is_read': read_hits.filter(sso_id=request.user.pk).exists()
#         }
