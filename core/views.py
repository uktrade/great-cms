from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
