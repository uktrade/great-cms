from datetime import datetime
import json
import sentry_sdk

from django.http import Http404
from django.views.generic import TemplateView, FormView
from django.utils.functional import cached_property
from django.shortcuts import redirect
from django.urls import reverse_lazy

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from requests.exceptions import RequestException

from directory_constants.choices import INDUSTRIES
from directory_api_client.client import api_client

from exportplan import data, helpers, forms


class BaseExportPlanView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if self.slug not in data.SECTION_SLUGS:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def export_plan(self):
        return helpers.get_or_create_export_plan(self.request.user)

    def get_context_data(self, *args, **kwargs):
        industries = [name for id, name in INDUSTRIES]
        country_choices = [{'value': key, 'label': label} for key, label in helpers.get_madb_country_list()]
        return super().get_context_data(
            next_section=self.next_section,
            sections=data.SECTION_TITLES,
            export_plan=self.export_plan,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            *args, **kwargs)


class ExportPlanSectionView(BaseExportPlanView):

    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None

        index = data.SECTION_SLUGS.index(self.slug)
        return {
            'title': data.SECTION_TITLES[index + 1],
            'url': data.SECTION_URLS[index + 1],
        }


class ExportPlanTargetMarketsView(ExportPlanSectionView):
    template_name = 'exportplan/sections/target-markets.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            selected_sectors=json.dumps(self.export_plan.get('sectors', [])),
            target_markets=json.dumps(self.export_plan.get('target_markets', [])),
            datenow=datetime.now(),
        )


class ExportPlanBrandAndProductView(ExportPlanSectionView, FormView):
    form_class = forms.ExportPlanBrandAndProductForm
    success_url = reverse_lazy('exportplan:brand-and-product')

    def form_valid(self, form):
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=self.export_plan['pk'],
            data={'brand_product_details': form.cleaned_data}
        )
        return super().form_valid(form)

    def get_form_initial(self):
        return self.export_plan['brand_product_details']

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['initial'] = self.get_form_initial()
        return form_kwargs

    def get_context_data(self, *args, **kwargs):
        form_initial = self.get_form_kwargs()['initial']

        field_names = [field[0] for field in self.form_class.base_fields.items()]

        field_labels = [field[1].label for field in self.form_class.base_fields.items()]

        field_placeholders = [field[1].widget.attrs['placeholder'] for field in self.form_class.base_fields.items()]

        form_fields = [
            {'name': name, 'label': label, 'placeholder': placeholder}
            for name, label, placeholder in zip(field_names, field_labels, field_placeholders)
        ]

        return super().get_context_data(
            form_initial=json.dumps(form_initial),
            form_fields=json.dumps(form_fields),
            *args, **kwargs)


class UpdateExportPlanAPIView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        export_plan = helpers.get_or_create_export_plan(self.request.user)
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data=request.data
        )
        return Response({})


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
