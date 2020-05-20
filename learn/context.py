from django.conf import settings
from directory_constants import choices

from core.context import AbstractPageContextProvider
from core.models import CuratedListPage
from learn import helpers


class LessonPageContextProvider(AbstractPageContextProvider):
    template_name = 'learn/detail_page.html'

    @staticmethod
    def get_context_data(request, page):
        if settings.FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE:
            suggested_countries = helpers.get_suggested_countries_for_sector('Food and Drink')
        else:
            suggested_countries = helpers.get_suggested_countries_for_user(request)
        return {
            'topics': CuratedListPage.objects.sibling_of(page.get_parent()),
            'country_choices': [{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
            'suggested_countries': suggested_countries,
        }
