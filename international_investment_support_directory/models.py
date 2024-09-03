from directory_constants import expertise
from domestic.models import BaseContentPage


class InvestmentSupportDirectoryIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = []
    template = 'investment_support_directory/index.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]

        context.update(
            breadcrumbs=breadcrumbs,
            CHOICES_FINANCIAL=expertise.FINANCIAL,
            CHOICES_HUMAN_RESOURCES=expertise.HUMAN_RESOURCES,
            CHOICES_LEGAL=expertise.LEGAL,
            CHOICES_PUBLICITY=expertise.PUBLICITY,
            CHOICES_BUSINESS_SUPPORT=expertise.BUSINESS_SUPPORT,
            CHOICES_MANAGEMENT_CONSULTING=expertise.MANAGEMENT_CONSULTING,
        )
        self.set_ga360_payload(
            page_id='Index',
            business_unit='Investment Support Directory',
            site_section='index',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload
        return context
