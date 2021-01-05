from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from cms_extras.views import case_study as case_study_view

app_name = 'cms_extra'


urlpatterns = [
    path('case-study/<int:case_study_id>/', staff_member_required(case_study_view), name='case-study-view'),
]
