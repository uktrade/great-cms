from django.urls import path

from learn import views

app_name = 'learn'

urlpatterns = [
    path('', views.LearnLandingPageView.as_view(), name='index'),
]
