from django.views.generic import ListView

from export_academy import models


class EventListView(ListView):
    model = models.Event
