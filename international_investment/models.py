from domestic.models import BaseContentPage


class InvestmentIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = []
    template = 'investment/index.html'
