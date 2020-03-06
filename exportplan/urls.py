from django.urls import path

from exportplan import views

app_name = 'exportplan'

urlpatterns = [
    path('', views.ExportPlanLandingPageView.as_view(), name='index'),
    path('dashboard/', views.ExportPlanBuilderLandingPageView.as_view(), name='landing-page'),
    path('about-your-business/', views.ExportPlanBuilderSectionView.as_view(), name='about-your-business'),
    path('start/', views.ExportPlanStartView.as_view(), name='start'),
    path('create/', views.ExportPlanCreateView.as_view(), name='create'),

]
