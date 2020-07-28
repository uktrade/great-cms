import wagtail_factories
from factory import fuzzy
from domestic.models import DomesticHomePage, DomesticDashboard


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'homepage'
    body = fuzzy.FuzzyText(length=255)
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticHomePage


class DomesticDashboardFactory(wagtail_factories.PageFactory):
    title = 'dashboard'
    live = True
    slug = 'dashboard'

    class Meta:
        model = DomesticDashboard
