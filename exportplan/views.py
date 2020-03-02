from django.views.generic import TemplateView
from .data import SECTION_TITLES


class ExportPlanLandingPageView(TemplateView):
    template_name = 'exportplan/landing_page.html'


class BaseExportPlanView(TemplateView):
    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            sections=SECTION_TITLES,
            *args, **kwargs)


class ExportPlanBuilderLandingPageView(BaseExportPlanView):
    template_name = 'exportplan/builder_landing_page.html'


class ExportPlanBuilderSectionView(BaseExportPlanView):
    template_name = 'exportplan/builder_section.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            title=SECTION_TITLES[0],
            *args, **kwargs
        )
