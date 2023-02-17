from django.views.generic import TemplateView


class IOOIndex(TemplateView):
    template_name = 'ioo/index.html'


class IOOSector(TemplateView):
    template_name = 'ioo/triage/sector.html'
