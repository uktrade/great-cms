import pickle

from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from domestic_growth.mixins import TriageMixin
from domestic_growth.forms import StartingABusinessForm, ScalingABusinessForm
from domestic_growth.helpers import get_postcode_data


class StartingABusinessView(TriageMixin, FormView):
    form_class = StartingABusinessForm
    template_name = 'starting-a-business.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )

    def get_success_url(self):
        qs = ''

        if self.request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('domestic_growth_triage_data')))[0]
            postcode = form_data.get('postcode')
            sector = form_data.get('sector')

            qs = f'?postcode={postcode}&sector={sector}'

        return f'/starting-a-business-guide{qs}'

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


class ScalingABusinessView(TriageMixin, FormView):
    form_class = ScalingABusinessForm
    template_name = 'scaling-a-business.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )

    def get_success_url(self):
        qs = ''

        if self.request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('domestic_growth_triage_data')))[0]
            postcode = form_data.get('postcode')
            sector = form_data.get('sector')

            qs = f'?postcode={postcode}&sector={sector}'

        return f'/growing-a-business-guide{qs}'

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)
