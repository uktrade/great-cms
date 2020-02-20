from directory_constants import choices
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from core import forms, helpers, permissions, serializers


class ExportPlanStartView(FormView):
    template_name = 'core/exportplanstart.html'
    form_class = forms.ExportPlanFormStart
    success_url = reverse_lazy('core:exportplan-view')

    def get_initial(self):
        return {
            'country': self.request.GET.get('country'),
            'commodity': self.request.GET.get('commodity code'),
        }

    def get_context_data(self, **kwargs):
        rules_regulation = None
        if self.request.GET.get('country'):
            rules_regulation = helpers.get_rules_and_regulations(self.request.GET['country'])
        return super().get_context_data(rules_regulation=rules_regulation, **kwargs)

    def form_valid(self, form):
        rules_regulation = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        helpers.create_export_plan(
            sso_session_id=self.request.user.session_id,
            exportplan_data=self.serialize_exportplan_data(rules_regulation)
        )
        return super().form_valid(form)

    def serialize_exportplan_data(self, exportplan_data):
        return {
            'export_countries': [exportplan_data['Country']],
            'export_commodity_codes': [exportplan_data['Commodity code']],
            'rules_regulations': exportplan_data,
        }


class ExportPlanView(TemplateView):
    template_name = 'core/exportplanview.html'

    def get_context_data(self, **kwargs):
        rules_regulation = helpers.get_exportplan_rules_regulations(sso_session_id=self.request.user.session_id)
        return super().get_context_data(rules_regulation=rules_regulation, **kwargs)


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            industry_options=[{'value': key, 'label': label} for key, label in choices.SECTORS],
            events=helpers.get_dashboard_events(),
            export_opportunities=helpers.get_dashboard_export_opportunities(),
            **kwargs,
        )


class EnrolCompanyAPIView(generics.GenericAPIView):

    serializer_class = serializers.EnrolCompanySerializer
    permission_classes = [IsAuthenticated, permissions.HasNoCompany]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_data = {
            'sso_id': self.request.user.id,
            'company_email': self.request.user.email,
            'contact_email_address': self.request.user.email,
            'company_name': self.request.data.get('company_name', '<unknown>'),
            'expertise_industries': self.request.data['expertise_industries'],
            'expertise_countries': self.request.data.get('expertise_countries', {}),
        }
        helpers.create_company_profile(company_data)
        if 'first_name' in self.request.data:
            user_data = {
                'first_name': self.request.data['first_name'],
                'last_name': self.request.data['last_name'],
            }
            helpers.create_user_profile(data=user_data, sso_session_id=self.request.user.session_id)
        return Response(status=200)
