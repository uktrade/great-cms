from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users import helpers


class ProductsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = helpers.get_user_products(request.user.session_id)
        return Response(status=200, data=data)

    def post(self, request, *args, **kwargs):
        data = helpers.add_update_user_product(request.user.session_id, self.request.data)
        return Response(status=200, data=data)


class MarketsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = helpers.get_user_markets(request.user.session_id)
        return Response(status=200, data=data)

    def post(self, request, *args, **kwargs):
        data = helpers.add_update_user_market(request.user.session_id, self.request.data)
        return Response(status=200, data=data)
