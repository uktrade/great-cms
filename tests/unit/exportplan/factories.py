import wagtail_factories

from core import models
from exportplan import models as exportplan_models


class ExportPlanPageFactory(wagtail_factories.PageFactory):

    title = 'export plan'
    live = True
    slug = 'export-plan'
    template = 'exportplan/automated_list_page.html'
    description = 'some description'
    button_label = 'some button label'

    class Meta:
        model = models.ListPage
        django_get_or_create = ['slug', 'parent']


class ExportPlanPseudoDashboardPageFactory(wagtail_factories.PageFactory):

    title = 'export plan detail-page pseudo-dashboard'
    live = True
    slug = 'dashboard'
    template = 'exportplan/dashboard_page.html'

    class Meta:
        model = models.DetailPage
        django_get_or_create = ['slug', 'parent']


class ExportPlanDashboardPageFactory(wagtail_factories.PageFactory):

    title = 'export plan real dashboard'
    live = True
    slug = 'dashboard'

    class Meta:
        model = exportplan_models.ExportPlanDashboardPage
