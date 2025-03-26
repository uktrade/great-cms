from django.conf import settings
from django.urls import path
from great_components.decorators import skip_ga360

from domestic_growth import views

app_name = 'domestic_growth'

urlpatterns = []

if settings.FEATURE_DOMESTIC_GROWTH:
    urlpatterns += [
        path(
            'pre-start/location/',
            skip_ga360(views.StartingABusinessLocationFormView.as_view()),
            name='domestic-growth-pre-start-location',
        ),
        path(
            'pre-start/sector/',
            skip_ga360(views.StartingABusinessSectorFormView.as_view()),
            name='domestic-growth-pre-start-sector',
        ),
        path(
            'existing/location/',
            skip_ga360(views.ExistingBusinessLocationFormView.as_view()),
            name='domestic-growth-existing-location',
        ),
        path(
            'existing/sector/',
            skip_ga360(views.ExistingBusinessSectorFormView.as_view()),
            name='domestic-growth-existing-sector',
        ),
        path(
            'existing/setup/',
            skip_ga360(views.ExistingBusinessWhenSetupFormView.as_view()),
            name='domestic-growth-when-set-up',
        ),
        path(
            'existing/turnover/',
            skip_ga360(views.ExistingBusinessTurnoverFormView.as_view()),
            name='domestic-growth-existing-turnover',
        ),
        path(
            'existing/exporter/',
            skip_ga360(views.ExistingBusinessCurrentlyExportFormView.as_view()),
            name='domestic-growth-existing-exporter',
        ),
    ]
