from datetime import datetime
import json
import sentry_sdk

from django.http import Http404
from django.views.generic import TemplateView, FormView
from django.utils.functional import cached_property
from django.shortcuts import redirect
from django.urls import reverse_lazy

from requests.exceptions import RequestException

from directory_constants.choices import INDUSTRIES, COUNTRY_CHOICES
from directory_api_client.client import api_client
from exportplan import data, helpers, forms
from core.helpers import CountryDemographics


class ExportPlanMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.slug not in data.SECTION_SLUGS:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def export_plan(self):
        return helpers.get_or_create_export_plan(self.request.user)

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None

        index = data.SECTION_SLUGS.index(self.slug)
        return {
            'title': data.SECTION_TITLES[index + 1],
            'url': data.SECTION_URLS[index + 1],
        }

    def get_context_data(self, **kwargs):
        industries = [name for _, name in INDUSTRIES]
        country_choices = [{'value': key, 'label': label} for key, label in COUNTRY_CHOICES]

        return super().get_context_data(
            next_section=self.next_section,
            sections=data.SECTION_TITLES,
            export_plan=self.export_plan,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            **kwargs
        )


class ExportPlanSectionView(ExportPlanMixin, TemplateView):
    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']


class ExportPlanMarketingApproachView(ExportPlanMixin, FormView):
    form_class = forms.CountryDemographicsForm
    template_name = 'exportplan/sections/marketing-approach.html'
    slug = 'marketing-approach'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET or {}
        if data:
            kwargs['data'] = data
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid():
            country = CountryDemographics(form.cleaned_data['name'])
            context['country'] = country
            context['age_range'] = country.filter_age_range(form.cleaned_data['age_range'])
            context['united_kingdom'] = CountryDemographics('United Kingdom')
        return context


class ExportPlanTargetMarketsView(ExportPlanSectionView):
    template_name = 'exportplan/sections/target-markets.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            selected_sectors=json.dumps(self.export_plan.get('sectors', [])),
            target_markets=json.dumps(self.export_plan.get('target_markets', [])),
            datenow=datetime.now(),
        )


class FormContextMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        field_names = list(self.form_class.base_fields.keys())

        field_labels = [field.label for field in self.form_class.base_fields.values()]

        field_placeholders = [
            field.widget.attrs.get('placeholder', '') for field in self.form_class.base_fields.values()
        ]

        field_tooltip = [
            field.widget.attrs.get('tooltip', '') for field in self.form_class.base_fields.values()
        ]

        form_fields = [
            {'name': name, 'label': label, 'placeholder': placeholder, 'tooltip': tooltip}
            for name, label, placeholder, tooltip in zip(field_names, field_labels, field_placeholders, field_tooltip)
        ]

        context['form_initial'] = json.dumps(context['form'].initial)
        context['form_fields'] = json.dumps(form_fields)

        return context


class ExportPlanBrandAndProductView(FormContextMixin, ExportPlanSectionView, FormView):

    def get_initial(self):
        return self.export_plan['brand_product_details']

    form_class = forms.ExportPlanBrandAndProductForm
    success_url = reverse_lazy('exportplan:brand-and-product')


class ExportPlanTargetMarketsResearchView(FormContextMixin, ExportPlanSectionView, FormView):

    def get_initial(self):
        return self.export_plan['target_markets_research']

    form_class = forms.ExportPlanTargetMarketsResearchForm
    success_url = reverse_lazy('exportplan:target-markets-research')


class ExportPlanBusinessObjectivesView(FormContextMixin, ExportPlanSectionView, FormView):
    form_class = forms.ExportPlanBusinessObjectivesForm
    success_url = reverse_lazy('exportplan:objectives')

    def form_valid(self, form):
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=self.export_plan['pk'],
            data=form.cleaned_data
        )
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['objectives'] = json.dumps(self.export_plan['company_objectives'])
        return context


class BaseFormView(FormView):

    success_url = '/export-plan/dashboard/'

    def get_initial(self):
        return self.request.user.company.serialize_for_form()

    def form_valid(self, form):
        try:
            response = api_client.company.profile_update(
                sso_session_id=self.request.user.session_id,
                data=self.serialize_form(form)
            )
            response.raise_for_status()
        except RequestException:
            self.send_update_error_to_sentry(
                user=self.request.user,
                api_response=response
            )
            raise
        return redirect(self.success_url)

    def serialize_form(self, form):
        return form.cleaned_data

    @staticmethod
    def send_update_error_to_sentry(user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending
        sentry_sdk.set_user(
            {'hashed_uuid': user.hashed_uuid, 'user_email': user.email}
        )
        sentry_sdk.set_extra('api_response', str(api_response.content))
        sentry_sdk.capture_message('Updating company profile failed')


class LogoFormView(BaseFormView):
    def get_initial(self):
        return {}
    form_class = forms.LogoForm
    template_name = 'exportplan/logo-form.html'
    success_message = 'Logo updated'
