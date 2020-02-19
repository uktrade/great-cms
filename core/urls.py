from django.urls import path
from django.contrib.auth.decorators import login_required

import core.views

app_name = 'core'


urlpatterns = [
    path(
        'dashboard/',
        login_required(core.views.DashboardView.as_view(), login_url='/'),
        name='dashboard'
    ),
    path(
        'exportplan-start/',
        core.views.ExportPlanStartView.as_view(),
        name='exportplan-start'
    ),
    path(
        'exportplan-create/',
        core.views.ExportPlanView.as_view(),
        name='exportplan-view'
    ),
]
