from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from users import api

app_name = 'users'

SIGNUP_URL = reverse_lazy('core:signup')

urlpatterns = [
    path(
        'user-product/',
        skip_ga360(api.ProductsView.as_view()),
        name='api-user-product',
    ),
    path(
        'user-market/',
        skip_ga360(api.MarketsView.as_view()),
        name='api-user-market',
    ),
]
