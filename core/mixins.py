import logging
import pickle
from importlib import import_module

from django.conf import settings
from django.http import Http404
from django.utils import translation
from great_components import helpers as great_components_helpers

from core import cms_slugs

logger = logging.getLogger(__name__)


class WagtailAdminExclusivePageMixin:
    """
    Limits creation of pages in Wagtail's admin UI to only one instance of a specific type.
    """

    @classmethod
    def can_create_at(cls, parent):
        return super().can_create_at(parent) and not cls.objects.exists()


class EnableSegmentationMixin:
    # used by the page modal manager React component
    def get_context(self, request):
        if request.user.is_authenticated and 'startsurvey' in request.GET:
            request.user.set_user_questionnaire_answer(0, 'in-progress')
        return super().get_context(request)


class AnonymousUserRequired:
    # used by core.wagtail_hooks.anonymous_user_required
    anonymous_user_required_redirect_url = cms_slugs.DASHBOARD_URL


class AuthenticatedUserRequired:
    # used by core.wagtail_hooks.authenticated_user_required
    authenticated_user_required_redirect_url = cms_slugs.SIGNUP_URL


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
        self.ga360_payload['user_id'] = user.hashed_uuid if (is_logged_in and not user.is_superuser) else None
        self.ga360_payload['site_language'] = translation.get_language()


class PageTitleMixin:
    # used by views to set a page title attribute
    def get_page_title(self):
        return getattr(self, 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('page', {})['title'] = self.get_page_title()

        return context


class PrepopulateFormMixin:
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['initial'] = self.get_form_initial()
        return form_kwargs

    @property
    def guess_given_name(self):
        if self.request.user.is_authenticated:
            if self.request.user.first_name:
                return self.request.user.first_name
            elif self.request.user.company and self.request.user.company.data['postal_full_name']:
                name = self.request.user.company.data['postal_full_name']
                return name.split(' ')[0]

    @property
    def guess_family_name(self):
        if self.request.user.last_name:
            return self.request.user.last_name
        elif self.request.user.company and self.request.user.company.data['postal_full_name']:
            names = self.request.user.company.data['postal_full_name'].split(' ')
            return names[-1] if len(names) > 1 else None


class GetSnippetContentMixin:
    """View mixin to fetch an instance of the appropriate Snippet,
    identified by self.snippet_import_path and self.slug attributes on any
    class that implements this mixin

        `snippet_import_path` should be a dot-separated importlib-style path to the relevant class
        `slug` is a string, mapping to a unique value stored in the snippet's `slug` SlugField

    eg
        path(
        'domestic/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS,  # this may be provided as a view kwarg instead, if it varies
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-domestic-success',
    ),

    """

    @property
    def slug(self):
        return self.kwargs['slug']

    @property
    def snippet_import_path(self):
        return self.kwargs['snippet_import_path']

    def get_snippet_instance(self):
        path, model_name = self.snippet_import_path.rsplit('.', 1)
        module_ = import_module(path)
        snippet_class = getattr(module_, model_name)
        try:
            return snippet_class.objects.get(slug=self.slug)
        except snippet_class.DoesNotExist:
            logger.exception('Non-page CMS snippet is missing: see logged context. Raising 404.')
            raise Http404()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            content_snippet=self.get_snippet_instance(),
        )


class PreventCaptchaRevalidationMixin:
    """When get_all_cleaned_data() is called the forms are revalidated,
    which causes captcha to fail becuase the same captcha response from google
    is posted to google multiple times. This captcha response is a nonce, and
    so google complains the second time it's seen.

    This is worked around by removing captcha from the form before the view
    calls get_all_cleaned_data

    """

    should_ignore_captcha = False

    def render_done(self, *args, **kwargs):
        self.should_ignore_captcha = True
        return super().render_done(*args, **kwargs)

    def get_form(self, step=None, *args, **kwargs):
        form = super().get_form(step=step, *args, **kwargs)
        if step == self.steps.last and self.should_ignore_captcha:
            del form.fields['captcha']
        return form


class NotFoundOnDisabledFeature:
    def dispatch(self, *args, **kwargs):
        if not self.flag:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class MarketAccessFeatureFlagMixin(NotFoundOnDisabledFeature):
    @property
    def flag(self):
        return settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT


class GuidedJourneyMixin:
    initial_data = {}

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get('guided_journey_data')

        if data:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        return initial

    def save_data(self, form):
        cleaned_data = form.cleaned_data

        form_data = ({**self.initial_data, **cleaned_data},)
        form_data = pickle.dumps(form_data).hex()
        self.request.session['guided_journey_data'] = form_data

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        form_data = {}

        if self.request.session.get('guided_journey_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('guided_journey_data')))[0]

        if self.kwargs.get('edit'):
            button_text = 'Save'

        return super().get_context_data(
            **kwargs,
            button_text=button_text,
            session_data=form_data,
        )
