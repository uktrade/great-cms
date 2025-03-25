from urllib.parse import urlencode
from uuid import UUID, uuid4

from django.urls import reverse_lazy
from django.views.generic import FormView
from pydantic import HttpUrl

from domestic_growth.forms import (
    StartingABusinessLocationForm,
    StartingABusinessSectorForm,
)
from domestic_growth.models import StartingABusinessTriage
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class BaseTriageFormView(FormView):

    session_id: str = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.session_id = self.get_session_id()

    def get_session_id(self) -> str:
        """
        Returns a string to be used as a unique identifier for Domestic Growth triage records.
        The return value will either be a django session ID, an existing session ID from QS params
        or a UUIDv4. This is necessary to facilitate users who have not accepted cookies and
        therefore do not have a django request.session.session_key
        """
        if self.request.session.session_key:
            return self.request.session.session_key
        elif self.request.GET.get('session_id', False):
            return self.request.GET.get('session_id')
        else:
            return uuid4()

    def get_success_url(self, success_url: str, params: dict = {}) -> HttpUrl:
        """
        Accepts a success view name for example, 'domestic_growth:domestic-growth-starting-a-business-sector`
        and if we are using a uuid as opposed to a session_key appends a query string parameter
        """
        try:
            if type(self.session_id) is UUID or type(UUID(self.session_id)) is UUID:
                params = {'session_id': self.session_id, **params}
                return f'{success_url}?{urlencode(params)}'
        except ValueError as e:  # NOQA:F841
            # todo logging of invalid session id in URL. thrown by UUID constructor when invalid parameter passed.
            pass

        return success_url


class StartingABusinessLocationFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-location.html'
    form_class = StartingABusinessLocationForm


    def form_valid(self, form):
        if form.is_valid():
            StartingABusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    'postcode': form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_success_url(reverse_lazy('domestic_growth:domestic-growth-pre-start-sector'))


class StartingABusinessSectorFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-sector.html'
    form_class = StartingABusinessSectorForm

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)

        return super().get_context_data(
            **kwargs,
            autocomplete_sector_data=autocomplete_sector_data,
        )

    def form_valid(self, form):
        if form.is_valid():
            StartingABusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    'sector_id': form.cleaned_data['sector'],
                    'dont_know_sector': form.cleaned_data['dont_know_sector_yet'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_success_url('/support-in-uk/pre-start-guide/')
