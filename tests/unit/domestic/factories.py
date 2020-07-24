import wagtail_factories
from factory import fuzzy
from domestic.models import DomesticHomePage


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'homepage'
    body = fuzzy.FuzzyText(length=255)
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticHomePage
