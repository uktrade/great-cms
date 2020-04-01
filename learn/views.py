from django.views.generic import TemplateView


class LearnPageView(TemplateView):
    template_name = 'learn/learn_page.html'
