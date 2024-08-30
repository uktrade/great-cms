from django.urls import path

from international_buy_from_the_uk import views

app_name = 'international_buy_from_the_uk'

urlpatterns = [
    path(
        'contact/',
        views.ContactView.as_view(),
        name='contact',
    ),
    path(
        'find-a-supplier/',
        views.FindASupplierSearchView.as_view(),
        name='find-a-supplier',
    ),
    path(
        'find-a-supplier/supplier/<slug:company_number>/',
        views.FindASupplierProfileView.as_view(),
        name='find-a-supplier-profile',
    ),
    path(
        'find-a-supplier/supplier/case-study/<slug:case_study_id>/',
        views.FindASupplierCaseStudyView.as_view(),
        name='find-a-supplier-case-study',
    ),
    path(
        'find-a-supplier/supplier/<slug:company_number>/contact/',
        views.FindASupplierContactView.as_view(),
        name='find-a-supplier-contact',
    ),
]
