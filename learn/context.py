from directory_constants import choices

from core.context import AbstractPageContextProvider
from core.models import ListPage
from learn import helpers


class LessonPageContextProvider(AbstractPageContextProvider):
    template_name = 'learn/lesson_page.html'

    @staticmethod
    def get_context_data(request, page):
        return {
            'topics': ListPage.objects.sibling_of(page.get_parent()).filter(template='learn/topic_page.html'),
            'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
            'suggested_countries': self.get_suggested_countries(request),
        }

    @staticmethod
    def get_suggested_countries(request):
        if request.user.is_authenticated:
            company = request.user.company
            if company and company.expertise_industries_labels:
                sector_label = company.expertise_industries_labels[0]
                return helpers.get_suggested_countries(sector_label)
        return []
