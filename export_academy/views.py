from django.views.generic import ListView, RedirectView

from export_academy import models


class LandingPageView(RedirectView):
    pattern_name = 'export_academy:upcoming-events'


class EventListView(ListView):
    model = models.Event
