from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

import core.mixins
from core import helpers
import core.forms


class ExportPlanStartView(FormView):
    template_name = 'core/exportplanstart.html'
    form_class = core.forms.ExportPlanFormStart
    success_url = reverse_lazy('core:exportplan-start')

    def get_initial(self):
        return {
            'country': self.request.GET.get('country'),
            'commodity': self.request.GET.get('commodity code'),
        }

    def get_context_data(self, **kwargs):
        rules_regulation = None
        if self.request.GET.get('country'):
            rules_regulation = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        return super().get_context_data(rules_regulation=rules_regulation, **kwargs)

    def form_valid(self, form):
        rules_regulation = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        helpers.create_export_plan(
            sso_session_id=self.request.user.session_id,
            exportplan_data=self.serialize_exportplan_data(rules_regulation)
        )
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.method == 'POST':
            return reverse_lazy('core:exportplan-view')

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
