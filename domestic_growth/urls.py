from django.conf import settings
from django.urls import path
from great_components.decorators import skip_ga360

from domestic_growth import views

app_name = 'domestic_growth'

urlpatterns = []

if settings.FEATURE_DOMESTIC_GROWTH:
    urlpatterns += [
        path(
            'support-in-uk/pre-start/location/',
            skip_ga360(views.StartingABusinessLocationFormView.as_view()),
            name='domestic-growth-pre-start-location',
        ),
        path(
            'support-in-uk/pre-start/sector/',
            skip_ga360(views.StartingABusinessSectorFormView.as_view()),
            name='domestic-growth-pre-start-sector',
        ),
        path(
            'support-in-uk/existing/location/',
            skip_ga360(views.ExistingBusinessLocationFormView.as_view()),
            name='domestic-growth-existing-location',
        ),
        path(
            'support-in-uk/existing/sector/',
            skip_ga360(views.ExistingBusinessSectorFormView.as_view()),
            name='domestic-growth-existing-sector',
        ),
        path(
            'support-in-uk/existing/set-up/',
            skip_ga360(views.ExistingBusinessWhenSetupFormView.as_view()),
            name='domestic-growth-when-set-up',
        ),
        path(
            'support-in-uk/existing/turnover/',
            skip_ga360(views.ExistingBusinessTurnoverFormView.as_view()),
            name='domestic-growth-existing-turnover',
        ),
        path(
            'support-in-uk/existing/exporter/',
            skip_ga360(views.ExistingBusinessCurrentlyExportFormView.as_view()),
            name='domestic-growth-existing-exporter',
        ),
    ]
