import pickle

from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from domestic_growth.forms import ScalingABusinessForm, StartingABusinessForm
from domestic_growth.helpers import get_postcode_data
from domestic_growth.mixins import TriageMixin


class LandingView(TriageMixin, TemplateView):
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )


class StartingABusinessView(TriageMixin, FormView):
    form_class = StartingABusinessForm
    template_name = 'starting-a-business.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )

    def get_success_url(self):
        return reverse_lazy('domestic_growth:domestic-growth-starting-a-business-results')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class StartingABusinessResultsView(TriageMixin, TemplateView):
    template_name = 'starting-a-business-results.html'

    def get_context_data(self, **kwargs):
        constituency = None
        council = None
        sector = None

        sector_content = {
            'Advanced manufacturing': [
                'Advanced manufacturing 1',
                'Advanced manufacturing 2',
                'Advanced manufacturing 3',
            ],
            'Aerospace': ['Aerospace 1', 'Aerospace 2', 'Aerospace 3'],
            'Food and drink': ['Food and drink 1', 'Food and drink 2', 'Food and drink 3'],
        }

        if self.request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('domestic_growth_triage_data')))[0]
            postcode = form_data.get('postcode')
            sector = form_data.get('sector')

            data = get_postcode_data(postcode)

            constituency = data.get('result').get('parliamentary_constituency_2024')
            council = data.get('result').get('admin_district')

        return super().get_context_data(
            **kwargs,
            constituency=constituency,
            council=council,
            growth_hub={'name': 'The Growth Hub'},
            sector_content=sector_content.get(sector),
        )


class ScalingABusinessView(TriageMixin, FormView):
    form_class = ScalingABusinessForm
    template_name = 'scaling-a-business.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )

    def get_success_url(self):
        return reverse_lazy('domestic_growth:domestic-growth-scaling-a-business-results')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class ScalingABusinessResultsView(TriageMixin, TemplateView):
    template_name = 'scaling-a-business-results.html'

    def get_context_data(self, **kwargs):
        constituency = None
        council = None
        sector = None

        sector_content = {
            'Advanced manufacturing': [
                'Advanced manufacturing 1',
                'Advanced manufacturing 2',
                'Advanced manufacturing 3',
            ],
            'Aerospace': ['Aerospace 1', 'Aerospace 2', 'Aerospace 3'],
            'Food and drink': ['Food and drink 1', 'Food and drink 2', 'Food and drink 3'],
        }

        if self.request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('domestic_growth_triage_data')))[0]
            postcode = form_data.get('postcode')
            sector = form_data.get('sector')

            data = get_postcode_data(postcode)

            constituency = data.get('result').get('parliamentary_constituency_2024')
            council = data.get('result').get('admin_district')

        return super().get_context_data(
            **kwargs,
            constituency=constituency,
            council=council,
            growth_hub={'name': 'The Growth Hub'},
            sector_content=sector_content.get(sector),
        )
