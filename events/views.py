from django.views.generic import ListView

from events import models


class EventListView(ListView):
    model = models.Event
