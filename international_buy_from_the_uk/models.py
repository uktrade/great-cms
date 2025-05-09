from django.shortcuts import render

from core.helpers import international_url
from domestic.models import BaseContentPage
from international_buy_from_the_uk.forms import IndexSearchForm


class BuyFromTheUKIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = []
    template = 'buy_from_the_uk/index.html'

    def serve(self, request, *args, **kwargs):
        form = IndexSearchForm()

        # Set breadcrumbs and render the page
        breadcrumbs = [
            {'name': 'Home', 'url': f'/{international_url(request)}/'},
        ]
        return render(
            request,
            'buy_from_the_uk/index.html',
            {
                'form': form,
                'page': self,
                'breadcrumbs': breadcrumbs,
            },
        )
