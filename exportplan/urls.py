from django.urls import path

from exportplan import views

app_name = 'exportplan'

urlpatterns = [
    path('', views.ExportPlanLandingPageView.as_view(), name='index'),
    path('dashboard/', views.ExportPlanBuilderLandingPageView.as_view(), name='landing-page'),
    path('about-your-business/', views.ExportPlanBuilderSectionView.as_view(), name='about-your-business'),
]
