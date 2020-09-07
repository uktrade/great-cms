import json
import sentry_sdk

from django.http import Http404
from django.views.generic import TemplateView, FormView
from django.utils.functional import cached_property
from django.shortcuts import redirect
from django.urls import reverse_lazy

from requests.exceptions import RequestException

from directory_constants.choices import INDUSTRIES, COUNTRY_CHOICES, MARKET_ROUTE_CHOICES, PRODUCT_PROMOTIONAL_CHOICES
from directory_api_client.client import api_client
from exportplan import data, helpers, forms


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


class LessonDetailsMixin:

    @property
    def lesson_details(self):
        return helpers.get_all_lesson_details()

    def get_context_data(self, **kwargs):

        return super().get_context_data(
            lesson_details=self.lesson_details,
            **kwargs
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

        field_example = [
            field.widget.attrs.get('example', '') for field in self.form_class.base_fields.values()
        ]

        field_description = [
            field.widget.attrs.get('description', '') for field in self.form_class.base_fields.values()
        ]

        field_currency = [
            field.widget.attrs.get('currency', '') for field in self.form_class.base_fields.values()
        ]

        field_choices = [
            field.choices if hasattr(field, 'choices') else '' for field in
            self.form_class.base_fields.values()
        ]

        field_types = [
            type(field.widget).__name__ for field in self.form_class.base_fields.values()
        ]

        form_fields = [
            {'name': name, 'label': label, 'field_type': field_type, 'placeholder': placeholder,
             'tooltip': tooltip, 'example': example,'description': description, 'currency': currency,
             'choices': choices}
            for
            name, label, field_type, placeholder, tooltip, example, description, currency, choices
            in zip(
                field_names, field_labels, field_types, field_placeholders, field_tooltip,
                field_example, field_description,
                field_currency, field_choices)
        ]

        context['form_initial'] = json.dumps(context['form'].initial)
        context['form_fields'] = json.dumps(form_fields)

        return context


class ExportPlanSectionView(ExportPlanMixin, TemplateView):
    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']


class ExportPlanMarketingApproachView(FormContextMixin, ExportPlanSectionView, FormView):
    form_class = forms.ExportPlanMarketingApproachForm
    slug = 'marketing-approach'

    def get_initial(self):
        return self.export_plan['marketing_approach']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_choices = [{'value': key, 'label': label} for key, label in MARKET_ROUTE_CHOICES]
        promotional_choices = [{'value': key, 'label': label} for key, label in PRODUCT_PROMOTIONAL_CHOICES]
        context['route_to_markets'] = json.dumps(self.export_plan['route_to_markets'])
        context['route_choices'] = route_choices
        context['promotional_choices'] = promotional_choices
        return context


class ExportPlanAdaptationForTargetMarketView(FormContextMixin, ExportPlanSectionView, FormView):

    form_class = forms.ExportPlanAdaptationForTargetMarketForm
    success_url = reverse_lazy('exportplan:adaptation-for-your-target-market')

    def get_initial(self):
        return self.export_plan['adaptation_target_market']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['check_duties_link'] = helpers.get_check_duties_link(self.export_plan)
        # To do pass lanaguage from export_plan object rather then  hardcoded
        context['language_data'] = helpers.get_cia_world_factbook_data(country='Netherlands', key='people,languages')
        context['target_market_documents'] = json.dumps(self.export_plan['target_market_documents'])
        return context


class ExportPlanTargetMarketsResearchView(FormContextMixin, ExportPlanSectionView, FormView):

    form_class = forms.ExportPlanTargetMarketsResearchForm
    success_url = reverse_lazy('exportplan:target-markets-research')

    def get_initial(self):
        return self.export_plan['target_markets_research']


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


class ExportPlanAboutYourBusinessView(LessonDetailsMixin, FormContextMixin, ExportPlanSectionView, FormView):

    def get_initial(self):
        return self.export_plan['about_your_business']

    form_class = forms.ExportPlanAboutYourBusinessForm
    success_url = reverse_lazy('exportplan:about-your-business')


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
