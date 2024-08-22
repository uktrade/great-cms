from domestic.models import BaseContentPage


class BuyFromTheUKIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = []
    template = 'buy_from_the_uk/index.html'

    def get_context(self, request, *args, **kwargs):
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]
        context = super().get_context(request, *args, **kwargs)
        context.update(breadcrumbs=breadcrumbs)
        self.set_ga360_payload(
            page_id='Index',
            business_unit='Buy from the UK',
            site_section='index',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload
        return context
