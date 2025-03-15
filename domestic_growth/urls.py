from django.conf import settings
from django.urls import path
from core.decorators import skip_ga360

from domestic_growth import views

app_name = 'domestic_growth'

urlpatterns = []

if settings.FEATURE_DOMESTIC_GROWTH:
    urlpatterns += [
        path(
            'domestic-growth/starting-a-new-business',
            skip_ga360(views.StartingABusinessView.as_view()),
            name='domestic-growth-starting-a-business',
        ),
        path(
            'domestic-growth/starting-a-new-business/results',
            skip_ga360(views.StartingABusinessResultsView.as_view()),
            name='domestic-growth-starting-a-business-results',
        ),
        path(
            'domestic-growth/scaling-an-existing-business',
            skip_ga360(views.ScalingABusinessView.as_view()),
            name='domestic-growth-scaling-a-business',
        ),
        path(
            'domestic-growth/scaling-an-existing-business/results',
            skip_ga360(views.ScalingABusinessResultsView.as_view()),
            name='domestic-growth-scaling-a-business-results',
        ),
    ]
