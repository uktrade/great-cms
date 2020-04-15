import wagtail_factories

from core import models


class ExportPlanPageFactory(wagtail_factories.PageFactory):

    title = 'export plan'
    live = True
    slug = 'export-plan'
    template = 'exportplan/export_plan_page.html'

    class Meta:
        model = models.ListPage
        django_get_or_create = ['slug', 'parent']


class ExportPlanDashboardPageFactory(wagtail_factories.PageFactory):

    title = 'export plan dashboard'
    live = True
    slug = 'dashboard'
    template = 'exportplan/export_plan_dashboard_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']
