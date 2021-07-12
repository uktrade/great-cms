from profile.exops import helpers

from django.conf import settings
from django.views.generic import TemplateView
from requests.exceptions import HTTPError


class ExportOpportunitiesBaseView(TemplateView):
    template_name_not_exops_user = 'exops/is-not-exops-user.html'
    template_name_error = 'exops/opportunities-retrieve-error.html'

    exops_data = None
    opportunities_retrieve_error = False

    def dispatch(self, request, *args, **kwargs):
        try:
            self.exops_data = helpers.get_exops_data(request.user.hashed_uuid)
        except HTTPError:
            self.opportunities_retrieve_error = True
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self, *args, **kwargs):
        if self.exops_data is not None:
            template_name = self.template_name_exops_user
        elif self.opportunities_retrieve_error is True:
            template_name = self.template_name_error
        else:
            template_name = self.template_name_not_exops_user
        return [template_name]

    def get_context_data(self):
        search_url = settings.EXPORTING_OPPORTUNITIES_SEARCH_URL
        return {
            'exops_tab_classes': 'active',
            'exops_data': self.exops_data,
            'EXPORTING_OPPORTUNITIES_SEARCH_URL': search_url,
        }


class ExportOpportunitiesApplicationsView(ExportOpportunitiesBaseView):
    template_name_exops_user = 'exops/is-exops-user-applications.html'


class ExportOpportunitiesEmailAlertsView(ExportOpportunitiesBaseView):
    template_name_exops_user = 'exops/is-exops-user-email-alerts.html'
