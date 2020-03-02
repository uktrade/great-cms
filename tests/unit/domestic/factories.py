import wagtail_factories

from domestic import models


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    class Meta:
        model = models.DomesticHomePage
