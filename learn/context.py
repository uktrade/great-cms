from core.context import AbstractPageContextProvider
from core.models import CuratedListPage
from directory_constants import choices
from learn import helpers


class LessonPageContextProvider(AbstractPageContextProvider):
    template_name = 'learn/detail_page.html'

    @staticmethod
    def get_context_data(request, page):
        full_transcript = request.GET.get('fullTranscript')
        if full_transcript:
            bespoke_breadcrumbs = [
                {
                    'title': 'Back',
                    'url': page.url,
                },
            ]
        else:
            bespoke_breadcrumbs = [
                {
                    'title': 'Learn to export',
                    'url': '/learn/categories/',
                },
                {
                    'title': page.get_parent().get_parent().title,
                    'url': page.get_parent().get_parent().url,
                },
            ]

        return {
            'topics': CuratedListPage.objects.sibling_of(page.get_parent()),
            'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
            'suggested_countries': helpers.get_suggested_countries_for_user(request),
            'full_transcript': request.GET.get('fullTranscript'),
            'bespoke_breadcrumbs': bespoke_breadcrumbs,
        }
