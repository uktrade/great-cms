import wagtail_factories

from domestic_growth.models import (
    DomesticGrowthHomePage,
)


class DomesticGrowthHomePageFactory(wagtail_factories.PageFactory):
    title = 'homepage'
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticGrowthHomePage
