import wagtail_factories

from domestic import models


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'homepage'
    live = True

    class Meta:
        model = models.DomesticHomePage
