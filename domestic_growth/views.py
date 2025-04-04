from urllib.parse import urlencode
from uuid import UUID, uuid4

from django.db.models.base import Model
from django.urls import reverse_lazy
from django.views.generic import FormView
from pydantic import HttpUrl

from domestic_growth.choices import LESS_THAN_3_YEARS_AGO
from domestic_growth.constants import (
    ESTABLISHED_GUIDE_URL,
    PRE_START_GUIDE_URL,
    START_UP_GUIDE_URL,
)
from domestic_growth.forms import (
    ExistingBusinessCurrentlyExportForm,
    ExistingBusinessLocationForm,
    ExistingBusinessSectorForm,
    ExistingBusinessTurnoverForm,
    ExistingBusinessWhenSetUpForm,
    StartingABusinessLocationForm,
    StartingABusinessSectorForm,
)
from domestic_growth.helpers import get_triage_data_for_form_init
from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


class BaseTriageFormView(FormView):

    session_id: str = ''
    triage_model: Model = ExistingBusinessTriage
    triage_field_name: str = ''

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
        if self.request.GET.get('session_id', False):
            return self.request.GET.get('session_id')
        elif self.request.session.session_key:
            return self.request.session.session_key
        else:
            return uuid4()

    def get_url_with_optional_session_id_param(self, url: str, params: dict = {}) -> HttpUrl:
        """
        Accepts a success url and if we are using a uuid as opposed to a session_key appends a
        query string parameter
        """
        try:
            if type(self.session_id) is UUID or type(UUID(self.session_id)) is UUID:
                params = {'session_id': self.session_id, **params}
                return f'{url}?{urlencode(params)}'
        except ValueError as e:  # NOQA:F841
            # todo logging of invalid session id in URL. thrown by UUID constructor when invalid parameter passed.
            pass

        return url

    def get_initial(self):
        triage_data = get_triage_data_for_form_init(self.triage_model, self.session_id)
        if triage_data:
            return {self.triage_field_name: getattr(triage_data, self.triage_field_name, None)}


class StartingABusinessLocationFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-location.html'
    form_class = StartingABusinessLocationForm
    triage_model = StartingABusinessTriage
    triage_field_name = 'postcode'

    def form_valid(self, form):
        if form.is_valid():
            StartingABusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    self.triage_field_name: form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-pre-start-sector')
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)

        return {'back_url': '/', **ctx_data}


class StartingABusinessSectorFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-sector.html'
    form_class = StartingABusinessSectorForm
    triage_model = StartingABusinessTriage

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)
        back_url = self.get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-pre-start-location')
        )

        return super().get_context_data(**kwargs, autocomplete_sector_data=autocomplete_sector_data, back_url=back_url)

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
        return super().get_url_with_optional_session_id_param(PRE_START_GUIDE_URL)

    def get_initial(self):
        triage_data = get_triage_data_for_form_init(StartingABusinessTriage, self.session_id)
        if triage_data:
            return {
                'sector': getattr(triage_data, 'sector_id', None),
                'dont_know_sector_yet': getattr(triage_data, 'dont_know_sector', None),
            }


class ExistingBusinessLocationFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-location.html'
    form_class = ExistingBusinessLocationForm
    triage_field_name = 'postcode'

    def form_valid(self, form):
        if form.is_valid():
            ExistingBusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    self.triage_field_name: form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-sector')
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)

        return {'back_url': '/', **ctx_data}


class ExistingBusinessSectorFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-sector.html'
    form_class = ExistingBusinessSectorForm

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)
        back_url = self.get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-location')
        )

        return super().get_context_data(**kwargs, autocomplete_sector_data=autocomplete_sector_data, back_url=back_url)

    def form_valid(self, form):
        if form.is_valid():
            ExistingBusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    'sector_id': form.cleaned_data['sector'],
                    'cant_find_sector': form.cleaned_data['cant_find_sector'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-when-set-up')
        )

    def get_initial(self):
        triage_data = get_triage_data_for_form_init(ExistingBusinessTriage, self.session_id)
        if triage_data:
            return {
                'sector': getattr(triage_data, 'sector_id', None),
                'cant_find_sector': getattr(triage_data, 'cant_find_sector', None),
            }


class ExistingBusinessWhenSetupFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-when-set-up.html'
    form_class = ExistingBusinessWhenSetUpForm
    triage_field_name = 'when_set_up'

    def form_valid(self, form):
        if form.is_valid():
            ExistingBusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    self.triage_field_name: form.cleaned_data['when_set_up'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-turnover')
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-sector')
        )

        return {'back_url': back_url, **ctx_data}


class ExistingBusinessTurnoverFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-turnover.html'
    form_class = ExistingBusinessTurnoverForm
    triage_field_name = 'turnover'

    def form_valid(self, form):
        if form.is_valid():
            ExistingBusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    self.triage_field_name: form.cleaned_data['turnover'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-exporter')
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-when-set-up')
        )

        return {'back_url': back_url, **ctx_data}


class ExistingBusinessCurrentlyExportFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-currently-export.html'
    form_class = ExistingBusinessCurrentlyExportForm
    triage_field_name = 'currently_export'

    def form_valid(self, form):
        if form.is_valid():
            ExistingBusinessTriage.objects.update_or_create(
                session_id=self.session_id,
                defaults={
                    self.triage_field_name: True if form.cleaned_data['currently_export'] == 'YES' else False,
                },
            )

        return super().form_valid(form)

    def get_success_url(self):

        triage_data = ExistingBusinessTriage.objects.get(session_id=self.session_id)

        success_url = ESTABLISHED_GUIDE_URL

        if triage_data and triage_data.when_set_up == LESS_THAN_3_YEARS_AGO:
            success_url = START_UP_GUIDE_URL

        return super().get_url_with_optional_session_id_param(success_url)

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_session_id_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-turnover')
        )

        return {'back_url': back_url, **ctx_data}

    def get_initial(self):
        triage_data = get_triage_data_for_form_init(ExistingBusinessTriage, self.session_id)
        if triage_data:
            return {
                self.triage_field_name: 'YES' if getattr(triage_data, self.triage_field_name, False) else 'NO',
            }
