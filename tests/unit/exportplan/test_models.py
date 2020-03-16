from wagtail.tests.utils import WagtailPageTests

from exportplan import models
from domestic.models import DomesticHomePage


class ExportPlanPageTests(WagtailPageTests):

    def test_can_be_created_under_domestic_home_page(self):
        self.assertAllowedParentPageTypes(models.ExportPlanPage, {DomesticHomePage})


class ExportPlanHomePageTests(WagtailPageTests):

    def test_can_be_created_under_exportplan_home_page(self):
        self.assertAllowedParentPageTypes(models.ExportPlanDashboardPage, {models.ExportPlanPage})
