from urllib.parse import urlencode
from uuid import UUID, uuid4

import sentry_sdk
from django.core.cache import cache
from django.db.models.base import Model
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from pydantic import HttpUrl

from core.fern import Fern
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
from domestic_growth.helpers import get_triage_data, persist_to_cache, persist_to_db
from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage
from international_online_offer.core import region_sector_helpers
from international_online_offer.services import get_dbt_sectors


@method_decorator(never_cache, name='dispatch')
class BaseTriageFormView(FormView):

    triage_uuid: str = ''
    triage_model: Model = ExistingBusinessTriage
    triage_field_name: str = ''
    cache_key: str = ''
    fern = Fern()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.triage_uuid = self.get_triage_uuid()
        model_str = (
            'ExistingBusinessTriage' if self.triage_model is ExistingBusinessTriage else 'StartingABusinessTriage'
        )
        self.cache_key = f'bgs:{model_str}:{self.triage_uuid}'

    def get_triage_uuid(self) -> str:
        """
        Returns a string to be used as a unique identifier for Domestic Growth triage records.
        The return value will either be a django session ID, an existing session ID from QS params
        or a UUIDv4. This is necessary to facilitate users who have not accepted cookies and
        therefore do not have a django request.session.session_key
        """
        if self.request.GET.get('triage_uuid'):
            return self.fern.decrypt(self.request.GET.get('triage_uuid'))
        elif self.request.session.session_key:
            return self.request.session.session_key
        else:
            return uuid4()

    def get_url_with_optional_triage_uuid_param(self, url: str, params: dict = {}) -> HttpUrl:
        """
        Accepts a success url and if we are using a uuid as opposed to a session_key appends a
        query string parameter. An exception is thrown if we try and instantiate UUID with
        a string that is not valid.
        """
        try:
            if type(self.triage_uuid) is UUID or type(UUID(self.triage_uuid)) is UUID:
                params = {'triage_uuid': self.fern.encrypt(str(self.triage_uuid)), **params}
                return f'{url}?{urlencode(params)}'
        except ValueError as e:  # NOQA:F841
            sentry_sdk.capture_exception(e)

        return f'{url}?{urlencode(params)}' if params else url

    def get_initial(self, triage_field_name=None) -> dict:
        if not triage_field_name:
            triage_field_name = self.triage_field_name

        # only try and get initial data from db if the user is editing which implies there is data to begin with
        if self.request.GET.get('edit'):

            # try getting data from cache so back button pre-populates form correctly otherwise db
            triage_data_from_cache = cache.get(self.cache_key)

            if triage_data_from_cache and triage_data_from_cache.get(triage_field_name):
                return {triage_field_name: triage_data_from_cache.get(triage_field_name)}
            else:
                triage_data_from_db = get_triage_data(self.triage_model, self.triage_uuid)

                if triage_data_from_db:
                    return {triage_field_name: getattr(triage_data_from_db, triage_field_name, None)}

        return {triage_field_name: None}


class StartingABusinessLocationFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-location.html'
    form_class = StartingABusinessLocationForm
    triage_model = StartingABusinessTriage
    triage_field_name = 'postcode'

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {
                    self.triage_field_name: form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-pre-start-sector'),
            {'edit': True} if self.request.GET.get('edit') else {},
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = (
            f'{PRE_START_GUIDE_URL}?triage_uuid={Fern().encrypt(self.triage_uuid)}'
            if PRE_START_GUIDE_URL in self.request.META.get('HTTP_REFERER', [])
            else '/'
        )

        return {'back_url': back_url, **ctx_data}


class StartingABusinessSectorFormView(BaseTriageFormView):
    template_name = 'starting-a-business/triage-sector.html'
    form_class = StartingABusinessSectorForm
    triage_model = StartingABusinessTriage

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)
        back_url = self.get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-pre-start-location'), {'edit': True}
        )

        return super().get_context_data(**kwargs, autocomplete_sector_data=autocomplete_sector_data, back_url=back_url)

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {
                    'sector_id': form.cleaned_data['sector'],
                    'dont_know_sector': form.cleaned_data['dont_know_sector_yet'],
                },
            )

            # at the last point in the triage we persist to the database and remove from cache
            persist_to_db(self.cache_key, self.triage_model, self.triage_uuid)
            cache.delete(self.cache_key)

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(PRE_START_GUIDE_URL)

    def get_initial(self):
        if self.request.GET.get('edit'):
            triage_data = get_triage_data(StartingABusinessTriage, self.triage_uuid)
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
            persist_to_cache(
                self.cache_key,
                {
                    self.triage_field_name: form.cleaned_data['postcode'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-sector'),
            {'edit': True} if self.request.GET.get('edit') else {},
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        http_referer = self.request.META.get('HTTP_REFERER', [])
        back_url = '/'

        if START_UP_GUIDE_URL in http_referer:
            back_url = f'{START_UP_GUIDE_URL}?triage_uuid={Fern().encrypt(self.triage_uuid)}'
        elif ESTABLISHED_GUIDE_URL in http_referer:
            back_url = f'{ESTABLISHED_GUIDE_URL}?triage_uuid={Fern().encrypt(self.triage_uuid)}'

        return {'back_url': back_url, **ctx_data}


class ExistingBusinessSectorFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-sector.html'
    form_class = ExistingBusinessSectorForm

    def get_context_data(self, **kwargs):
        dbt_sectors = get_dbt_sectors()
        autocomplete_sector_data = region_sector_helpers.get_sectors_as_string(dbt_sectors)
        back_url = self.get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-location'), {'edit': True}
        )

        return super().get_context_data(**kwargs, autocomplete_sector_data=autocomplete_sector_data, back_url=back_url)

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {
                    'sector_id': form.cleaned_data['sector'],
                    'cant_find_sector': form.cleaned_data['cant_find_sector'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-when-set-up'),
            {'edit': True} if self.request.GET.get('edit') else {},
        )

    def get_initial(self):
        if self.request.GET.get('edit'):
            triage_sector = super().get_initial(triage_field_name='sector_id')
            triage_cant_find_sector = super().get_initial(triage_field_name='cant_find_sector')

            if triage_sector or triage_cant_find_sector:
                return {
                    'sector': triage_sector.get('sector_id'),
                    'cant_find_sector': triage_cant_find_sector.get('cant_find_sector'),
                }


class ExistingBusinessWhenSetupFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-when-set-up.html'
    form_class = ExistingBusinessWhenSetUpForm
    triage_field_name = 'when_set_up'

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {
                    self.triage_field_name: form.cleaned_data['when_set_up'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-turnover'),
            {'edit': True} if self.request.GET.get('edit') else {},
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-sector'), {'edit': True}
        )

        return {'back_url': back_url, **ctx_data}


class ExistingBusinessTurnoverFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-turnover.html'
    form_class = ExistingBusinessTurnoverForm
    triage_field_name = 'turnover'

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {
                    self.triage_field_name: form.cleaned_data['turnover'],
                },
            )

        return super().form_valid(form)

    def get_success_url(self):
        return super().get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-exporter'),
            {'edit': True} if self.request.GET.get('edit') else {},
        )

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-when-set-up'), {'edit': True}
        )

        return {'back_url': back_url, **ctx_data}


class ExistingBusinessCurrentlyExportFormView(BaseTriageFormView):
    template_name = 'existing-business/triage-currently-export.html'
    form_class = ExistingBusinessCurrentlyExportForm
    triage_field_name = 'currently_export'

    def form_valid(self, form):
        if form.is_valid():
            persist_to_cache(
                self.cache_key,
                {self.triage_field_name: True if form.cleaned_data['currently_export'] == 'YES' else False},
            )

            # at the last point in the triage we persist to the database and remove from cache
            persist_to_db(self.cache_key, self.triage_model, self.triage_uuid)
            cache.delete(self.cache_key)

        return super().form_valid(form)

    def get_success_url(self):

        triage_data = ExistingBusinessTriage.objects.get(triage_uuid=self.triage_uuid)

        success_url = ESTABLISHED_GUIDE_URL

        if triage_data and triage_data.when_set_up == LESS_THAN_3_YEARS_AGO:
            success_url = START_UP_GUIDE_URL

        return super().get_url_with_optional_triage_uuid_param(success_url)

    def get_context_data(self, **kwargs):
        ctx_data = super().get_context_data(**kwargs)
        back_url = self.get_url_with_optional_triage_uuid_param(
            reverse_lazy('domestic_growth:domestic-growth-existing-turnover'), {'edit': True}
        )

        return {'back_url': back_url, **ctx_data}

    def get_initial(self):
        if self.request.GET.get('edit'):
            triage_currently_export = super().get_initial(triage_field_name='currently_export')

            if triage_currently_export and triage_currently_export.get(self.triage_field_name) is not None:
                return {
                    self.triage_field_name: (
                        'YES' if triage_currently_export.get(self.triage_field_name) is True else 'NO'
                    ),
                }
