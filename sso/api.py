from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import DetailPage
from sso import helpers, serializers


class LessonCompletedAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_id = request.user.session_id
        lesson_obj = DetailPage.objects.get(pk=kwargs['lesson'])
        response = helpers.set_lesson_completed(session_id, lesson_obj)
        return Response(status=200, data=response)

    def get(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.get_lesson_completed(session_id, kwargs['lesson'])
        return Response(status=200, data=response)

    def delete(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.delete_lesson_completed(session_id, kwargs['lesson'])
        return Response(status=status.HTTP_204_NO_CONTENT, data=response)


class UserProfileAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.update_user_profile(session_id, request.data)

        return Response(status=200, data=response)


class QuestionnaireAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = request.user.get_user_questionnaire()
        return Response(status=200, data=response)

    @extend_schema(request=serializers.QuestionnaireSerializer)
    def post(self, request, *args, **kwargs):
        response = request.user.set_user_questionnaire_answer(
            question_id=request.data.get('questionId'), answer=request.data.get('answer')
        )
        return Response(status=200, data=response)


class UserDataAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserDataSerializer
    user_products_serializer_class = serializers.UserProductsSerializer

    def get_serializer_class(self):
        user_data_type = self.kwargs['name']

        if user_data_type in ('UserProducts', 'ActiveProduct'):
            serializer = self.user_products_serializer_class
        else:
            serializer = super().get_serializer_class()

        return serializer

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        response = request.user.get_user_data(name=kwargs['name'])
        return Response(status=200, data=response)

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        serializer = self.get_serializer(data=data, many=isinstance(data, list))
        serializer.is_valid(raise_exception=True)

        response = request.user.set_user_data(data=data, name=kwargs['name'])

        return Response(status=200, data=response)
