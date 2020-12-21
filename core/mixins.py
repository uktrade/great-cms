from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from great_components import helpers as great_components_helpers

from config import settings
from core import cms_slugs


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
                'steps': list(self.tour.steps.values('title', 'body', 'position', 'selector')),
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
    anonymous_user_required_redirect_url = cms_slugs.DASHBOARD_URL


class AuthenticatedUserRequired:
    # used by core.wagtail_hooks.authenticated_user_required
    authenticated_user_required_redirect_url = cms_slugs.LOGIN_URL


class WagtailGA360Mixin:
    """
    We can't use GA360Mixin.get_context_data() because that was for a
    view not a model, so this is duplicated code :o(

    This mixin pulls values relative to GA into the context and it's meant be
    used along in GA360Mixin inside the model's get_context() method.

    An example setup would look like:

    class DomesticDashboard(mixins.WagtailGA360Mixin, GA360Mixin, Page):
        ...
        def get_context(self, request):
            ...
            self.set_ga360_payload(
            page_id=self.id,
            business_unit=[BUSINESS_UNIT],
            site_section=[SITE_SECTION],
            )
            self.add_ga360_data_to_payload(request)
            context['ga360'] = self.ga360_payload
            ...
            return context
        ...
    """

    def add_ga360_data_to_payload(self, request):
        user = great_components_helpers.get_user(request)
        is_logged_in = great_components_helpers.get_is_authenticated(request)
        self.ga360_payload['login_status'] = is_logged_in
        self.ga360_payload['user_id'] = user.hashed_uuid if is_logged_in else None
        self.ga360_payload['site_language'] = translation.get_language()


class PageTitleMixin(object):
    # used by views to set a page_title attribute
    def get_page_title(self, context):
        return getattr(self, 'page_title', 'Welcome to great.gov.uk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title(context)

        return context
