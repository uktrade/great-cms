import wagtail_factories

from exportplan import models


class ExportPlanPageFactory(wagtail_factories.PageFactory):

    title = 'export plan'
    live = True
    slug = 'export-plan'

    class Meta:
        model = models.ExportPlanPage
        django_get_or_create = ['slug', 'parent']


class ExportPlanDashboardPageFactory(wagtail_factories.PageFactory):

    title = 'export plan dashboard'
    live = True
    slug = 'dashboard'

    class Meta:
        model = models.ExportPlanDashboardPage
        django_get_or_create = ['slug', 'parent']
