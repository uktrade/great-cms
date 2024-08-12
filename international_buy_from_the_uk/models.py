from domestic.models import BaseContentPage


class BuyFromTheUKIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = []
    template = 'buy_from_the_uk/index.html'
