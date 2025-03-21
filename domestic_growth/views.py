from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from domestic_growth.forms import (
    StartingABusinessLocationForm,
    StartingABusinessSectorForm,
)
from domestic_growth.mixins import TriageMixin
from domestic_growth.models import StartingABusinessUser
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class StartingABusinessLocationFormView(FormView):
    template_name = 'starting-a-business/triage-location.html'
    form_class = StartingABusinessLocationForm
    success_url = reverse_lazy('domestic_growth:domestic-growth-starting-a-business-sector')

    def form_valid(self, form):
        if form.is_valid():
            StartingABusinessUser.objects.update_or_create(
                session_key=self.request.session.session_key,
                defaults={
                    'postcode': form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)


class StartingABusinessSectorFormView(FormView):
    template_name = 'starting-a-business/triage-sector.html'
    form_class = StartingABusinessSectorForm
    success_url = reverse_lazy('domestic_growth:domestic-growth-starting-a-business-results')

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)

        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
        )

    def form_valid(self, form):
        if form.is_valid():
            StartingABusinessUser.objects.update_or_create(
                session_key=self.request.session.session_key,
                defaults={
                    'sector_id': form.cleaned_data['sector'],
                    'dont_know_sector': form.cleaned_data['dont_know_sector_yet'],
                },
            )

        return super().form_valid(form)


class StartingABusinessResultsView(TriageMixin, TemplateView):
    template_name = 'starting-a-business/results.html'
