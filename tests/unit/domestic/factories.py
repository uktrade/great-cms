import wagtail_factories

from domestic import models


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'domestic_homepage'
    live = True
    slug = 'homepage'

    class Meta:
        model = models.DomesticHomePage
        django_get_or_create = ['slug', 'parent']
