from django.views.generic import ListView, RedirectView, TemplateView

from export_academy import models


class EventListView(ListView):
    model = models.Event


class LandingPageView(RedirectView):
    template_name = 'landing.html'


class AboutView(TemplateView):
    template_name = 'landing.html'

    def get_context_data(self):
        return {'about_tab_classes': 'active'}
