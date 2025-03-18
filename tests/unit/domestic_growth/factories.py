import wagtail_factories

from domestic_growth.models import (
    DomesticGrowthChildGuidePage,
    DomesticGrowthGuidePage,
    DomesticGrowthHomePage,
)


class DomesticGrowthHomePageFactory(wagtail_factories.PageFactory):
    title = 'homepage'
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticGrowthHomePage


class DomesticGrowthGuidePageFactory(wagtail_factories.PageFactory):
    title = 'guidepage'
    live = True
    slug = 'guidepage'

    class Meta:
        model = DomesticGrowthGuidePage


class DomesticGrowthChildGuidePageFactory(wagtail_factories.PageFactory):
    title = 'child-guidepage'
    live = True
    slug = 'child-guidepage'

    class Meta:
        model = DomesticGrowthChildGuidePage
