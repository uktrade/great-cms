from django.core.exceptions import ObjectDoesNotExist
from core import constants
from config import settings


class WagtailAdminExclusivePageMixin:
    """
    Limits creation of pages in Wagtail's admin UI to only one instance of a specific type.
    """

    @classmethod
    def can_create_at(cls, parent):
        return super().can_create_at(parent) and not cls.objects.exists()


class EnableTourMixin:
    # exposes tour snippet to the template, used by the "tour guide" React component
    def get_context(self, request):
        context = super().get_context(request)
        try:
            context['tour'] = {
                'title': self.tour.title,
                'body': self.tour.body,
                'button_text': self.tour.button_text,
                'steps': list(self.tour.steps.values('title', 'body', 'position', 'selector'))
            }
        except ObjectDoesNotExist:
            pass
        return context


class ExportPlanMixin:
    # gets export plan data for use by the persionalization bar
    def get_context(self, request):
        context = super().get_context(request)
        if request.user and hasattr(request.user, 'export_plan'):
            context['export_plan'] = request.user.export_plan
        context['FEATURE_ENABLE_PRODUCT_SEARCH_WHEN_NO_USER'] = settings.FEATURE_ENABLE_PRODUCT_SEARCH_WHEN_NO_USER
        return context


class AnonymousUserRequired:
    # used by core.wagtail_hooks.anonymous_user_required
    anonymous_user_required_redirect_url = constants.DASHBOARD_URL


class AuthenticatedUserRequired:
    # used by core.wagtail_hooks.authenticated_user_required
    authenticated_user_required_redirect_url = constants.LOGIN_URL
