from django.urls import reverse_lazy
from django.views.generic import TemplateView


class LearnLandingPageView(TemplateView):
    template_name = 'learn/landing_page.html'
