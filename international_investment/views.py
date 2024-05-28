from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin

from international_investment.forms import (
    EstimateInvestment,
    InvestmentFund,
    InvestmentTypes,
)


class IndexView(GA360Mixin, TemplateView):
    template_name = 'investment/index.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Index',
            business_unit='Investment',
            site_section='index',
        )


class InvestmentFundView(GA360Mixin, FormView):
    form_class = InvestmentFund
    template_name = 'investment/investment_fund.html'
    success_url = reverse_lazy('international_investment:investment-types')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentFund',
            business_unit='Investment',
            site_section='investment-fund',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('international_investment:index')
        return context

    def form_valid(self, form):
        self.request.session = {**self.request.session, **form.cleaned_data}
        print(self.request.session)
        return super().form_valid(form)


class InvestmentTypesView(GA360Mixin, FormView):
    form_class = InvestmentTypes
    template_name = 'investment/investment_types.html'
    success_url = reverse_lazy('international_investment:estimate-investment')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentTypes',
            business_unit='Investment',
            site_section='investment-type',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('international_investment:investment-fund')
        return context

    def form_valid(self, form):
        self.request.session = {**self.request.session, **form.cleaned_data}
        print(self.request.session)
        return super().form_valid(form)


class EstimateInvestment(GA360Mixin, FormView):
    form_class = EstimateInvestment
    template_name = 'investment/estimate_investment.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentTypes',
            business_unit='Investment',
            site_section='investment-type',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('international_investment:investment-types')
        return context
