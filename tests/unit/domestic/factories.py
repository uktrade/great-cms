import wagtail_factories
import factory
import factory.fuzzy
from domestic.models import DomesticHomePage, DomesticDashboard
# from wagtail.tests.utils.form_data import streamfield
# from wagtail.core.fields import StreamField
# from wagtail.core import blocks
from core import blocks as core_blocks


class RouteSectionFactory(wagtail_factories.StructBlockFactory):
    title = 'Title'
    body = '345678638721683768723'
    image = None
    button = None

    class Meta:
        model = core_blocks.RouteSectionBlock


class DomesticHomePageFactory(wagtail_factories.PageFactory):

    title = 'homepage'
    body = factory.fuzzy.FuzzyText(length=255)
    live = True
    slug = 'homepage'

    class Meta:
        model = DomesticHomePage


class DomesticDashboardFactory(wagtail_factories.PageFactory):
    title = 'dashboard title'
    live = True
    slug = 'dashboard'
    """
    routes = streamfield([
        (RouteSectionFactory()),
        (RouteSectionFactory(Title='wibble')),
    ])
    """
    routes = wagtail_factories.StreamFieldFactory([
        RouteSectionFactory
    ]
    )

    class Meta:
        model = DomesticDashboard
