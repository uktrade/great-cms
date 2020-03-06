from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from exportplan import data, forms, helpers


class ExportPlanLandingPageView(TemplateView):
    template_name = 'exportplan/landing_page.html'


class BaseExportPlanView(TemplateView):
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            sections=data.SECTION_TITLES,
            *args, **kwargs)


class ExportPlanBuilderLandingPageView(BaseExportPlanView):
    template_name = 'exportplan/builder_landing_page.html'


class ExportPlanBuilderSectionView(BaseExportPlanView):
    template_name = 'exportplan/builder_section.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            title=data.SECTION_TITLES[0],
            *args, **kwargs
        )


class ExportPlanStartView(FormView):
    template_name = 'exportplan/start.html'
    form_class = forms.ExportPlanFormStart
    success_url = reverse_lazy('exportplan:index')

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


class ExportPlanCreateView(TemplateView):
    template_name = 'exportplan/create.html'

    def get_context_data(self, **kwargs):
        rules_regulation = helpers.get_exportplan_rules_regulations(sso_session_id=self.request.user.session_id)
        return super().get_context_data(rules_regulation=rules_regulation, **kwargs)
