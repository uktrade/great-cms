from django.urls import path

from international_investment_support_directory import views

app_name = 'international_investment_support_directory'

urlpatterns = [
    path(
        'find-a-specialist/',
        views.FindASpecialistSearchView.as_view(),
        name='find-a-specialist',
    ),
    path(
        'specialist/<slug:company_number>/',
        views.FindASpecialistProfileView.as_view(),
        name='specialist-profile',
    ),
    path(
        'specialist/case-study/<slug:case_study_id>/',
        views.FindASpecialistCaseStudyView.as_view(),
        name='specialist-case-study',
    ),
    path(
        'specialist/<slug:company_number>/contact/',
        views.FindASpecialistContactView.as_view(),
        name='specialist-contact',
    ),
]
