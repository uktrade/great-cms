from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib.messages.views import SuccessMessageMixin

import core.mixins

from directory_components import forms
from core import helpers
import core.forms


class ExportPlanStartView(FormView):
    template_name = 'ExportPlanStart.html'
    form_class = core.forms.ExportPlanFormStart
    success_url = reverse_lazy('core:exportplan-start')

    def get_initial(self):
        return {
            'country': self.request.GET.get('country'),
            'commodity': self.request.GET.get('commodity code'),
        }

    def get_context_data(self, **kwargs):
        rules_regs = None
        if self.request.GET.get('country'):
            rules_regs = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        return super().get_context_data(rules_regs=rules_regs, **kwargs)

    def form_valid(self, form):
        rules_regs = helpers.get_rules_and_regulations(self.request.GET.get('country'))
        helpers.create_export_plan(sso_session_id=self.request.user.session_id, exportplan_data=rules_regs)
        self.success_url = reverse_lazy('core:exportplan-view')
        return super().form_valid(form)


class ExportPlanView(TemplateView):
    template_name = 'ExportPlanView.html'

    def get_context_data(self, **kwargs):
        rules_regs = helpers.get_exportplan_rules_regulations(sso_session_id=self.request.user.session_id)
        return super().get_context_data(rules_regs=rules_regs, **kwargs)


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
