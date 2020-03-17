from django.urls import path

from exportplan import views

app_name = 'exportplan'

urlpatterns = [
    path('start/', views.ExportPlanStartView.as_view(), name='start'),
    path('create/', views.ExportPlanCreateView.as_view(), name='create'),
    path('target-markets/', views.ExportPlanBuilderSectionView.as_view(), name='target-markets'),
]
