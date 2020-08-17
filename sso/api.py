from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from sso import helpers


class LessonCompletedAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.set_lesson_completed(session_id, kwargs['lesson'])
        return Response(status=200, data=response)

    def get(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.get_lesson_completed(session_id, kwargs['lesson'])
        return Response(status=200, data=response)

    def delete(self, request, *args, **kwargs):
        session_id = request.user.session_id
        response = helpers.delete_lesson_completed(session_id, kwargs['lesson'])
        return Response(status=status.HTTP_204_NO_CONTENT, data=response)
