from django.views.generic import TemplateView
from great_components.mixins import GA360Mixin


class IndexView(GA360Mixin, TemplateView):
    template_name = 'investment/index.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Index',
            business_unit='Investment',
            site_section='index',
        )


class InvestmentFundView(GA360Mixin, TemplateView):
    template_name = 'investment/investment_fund.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentFund',
            business_unit='Investment',
            site_section='investment-fund',
        )
