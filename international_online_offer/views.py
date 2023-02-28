from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from international_online_offer import forms


class IOOIndex(TemplateView):
    template_name = 'ioo/index.html'


class IOOSector(FormView):
    form_class = forms.SectorForm
    template_name = 'ioo/triage/sector.html'
    success_url = reverse_lazy('international_online_offer:intent')


class IOOIntent(FormView):
    form_class = forms.IntentForm
    template_name = 'ioo/triage/intent.html'
    success_url = reverse_lazy('international_online_offer:location')


class IOOLocation(FormView):
    form_class = forms.LocationForm
    template_name = 'ioo/triage/location.html'
    success_url = reverse_lazy('international_online_offer:index')
