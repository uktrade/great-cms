import abc
import json
import logging

from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.contrib.sitemaps import Sitemap as DjangoSitemap
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView
from formtools.wizard.views import NamedUrlSessionWizardView
from great_components.mixins import GA360Mixin
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap

from core import cms_slugs, forms, helpers, serializers
from core.mixins import AuthenticatedUserRequired, PageTitleMixin
from core.models import GreatMedia
from directory_constants import choices
from domestic.models import DomesticDashboard, TopicLandingPage
from sso.views import SSOBusinessUserLogoutView

logger = logging.getLogger(__name__)

STEP_START = 'start'
STEP_WHAT_SELLING = 'what-are-you-selling'
STEP_PRODUCT_SEARCH = 'product-search'
STEP_SIGN_UP = 'sign-up'


class UpdateCompanyAPIView(generics.GenericAPIView):
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {key: value for key, value in serializer.validated_data.items() if value}
        if not self.request.user.company:
            data['name'] = f'unnamed sso-{self.request.user.id} company'
        helpers.update_company_profile(sso_session_id=self.request.user.session_id, data=data)
        return Response(status=200)


class ArticleView(GA360Mixin, FormView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='capability',
        )

    template_name = 'core/article.html'
    success_url = cms_slugs.DASHBOARD_URL
    form_class = forms.NoOperationForm

    def get_context_data(self):
        return super().get_context_data(
            topic_name=self.kwargs['topic'],
            chapter_name=self.kwargs['chapter'],
            article_name=self.kwargs['article'],
            country_choices=[{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
        )


class LoginView(GA360Mixin, PageTitleMixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='login',
        )

    template_name = 'core/login.html'
    title = 'Sign in'


class LogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.method == 'GET' and 'next' in self.request.GET:
            self.url = self.request.GET['next']
        else:
            self.url = settings.BASE_URL
        SSOBusinessUserLogoutView.post(self, self.request)
        return super().get_redirect_url(*args, **kwargs)


class SignupView(GA360Mixin, PageTitleMixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='signup',
        )

    template_name = 'core/signup.html'
    title = 'Sign up'


class CompareCountriesView(GA360Mixin, PageTitleMixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='TargetMarkets',
            business_unit='MagnaUnit',
            site_section='target markets',
        )

    template_name = 'core/compare_countries.html'
    title = 'Where to export'

    def get_context_data(self, **kwargs):
        dashboard = DomesticDashboard.objects.live().first()
        context = super().get_context_data(**kwargs)
        if self.request.user and hasattr(self.request.user, 'export_plan'):
            context['export_plan'] = self.request.user.export_plan.data
            context['data_tabs_enabled'] = json.dumps(settings.FEATURE_COMPARE_MARKETS_TABS)
            context['max_compare_places_allowed'] = settings.MAX_COMPARE_PLACES_ALLOWED
            context['dashboard_components'] = dashboard.components if dashboard else None
        return context


class CountriesView(generics.GenericAPIView):
    def get(self, request):
        return Response([c for c in choices.COUNTRIES_AND_TERRITORIES_REGION if c.get('type') == 'Country'])


class SuggestedCountriesView(generics.GenericAPIView):
    def get(self, request):
        hs_code = request.GET.get('hs_code')
        return Response(
            helpers.get_suggested_countries_by_hs_code(sso_session_id=self.request.user.session_id, hs_code=hs_code)
        )


def handler404(request, *args, **kwargs):
    return TemplateResponse(request=request, template='core/404.html', context={}, status=404)


def handler500(request, *args, **kwargs):
    return TemplateResponse(request=request, template='core/500.html', context={}, status=500)


class AbstractSignupWizardView(abc.ABC):
    step_labels = (
        'Get tailored content',
        'What are you selling?',
        'Find your product',
        'Sign up',
    )

    @property
    @abc.abstractmethod
    def templates(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def form_list(self):
        raise NotImplementedError

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def done(self, form_list, **kwargs):
        # react component handles the signing up, this wizard is just for data collection that is fed into
        # the react component on the final step, so this step should not be submitted to
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(step_labels=self.step_labels, **kwargs)
        if self.steps.current == STEP_SIGN_UP:
            context['product_search_data'] = self.get_cleaned_data_for_step(STEP_PRODUCT_SEARCH)
        return context

    def get_step_url(self, step):
        # we want to maintain the querystring params. e.g, next tells the final
        # step where to send the user
        url = super().get_step_url(step)
        if self.request.GET.get('next'):
            querystring = self.request.META['QUERY_STRING']
            if querystring:
                url = f'{url}?{querystring}'
        return url


class SignupForTailoredContentWizardView(GA360Mixin, AbstractSignupWizardView, NamedUrlSessionWizardView):
    extra_context = {'allow_skip_signup': True}
    templates = {
        STEP_START: 'core/signup-wizard-step-start-tailored-content.html',
        STEP_WHAT_SELLING: 'core/signup-wizard-step-what-selling.html',
        STEP_PRODUCT_SEARCH: 'core/signup-wizard-step-product-search.html',
        STEP_SIGN_UP: 'core/signup-wizard-step-sign-up.html',
    }

    form_list = (
        (STEP_START, forms.NoOperationForm),
        (STEP_WHAT_SELLING, forms.WhatAreYouSellingForm),
        (STEP_PRODUCT_SEARCH, forms.ProductSearchForm),
        (STEP_SIGN_UP, forms.NoOperationForm),
    )


class SignupForExportPlanWizardView(GA360Mixin, AbstractSignupWizardView, NamedUrlSessionWizardView):
    extra_context = {'allow_skip_signup': False}
    templates = {
        STEP_START: 'core/signup-wizard-step-start-export-plan.html',
        STEP_WHAT_SELLING: 'core/signup-wizard-step-what-selling.html',
        STEP_PRODUCT_SEARCH: 'core/signup-wizard-step-product-search.html',
        STEP_SIGN_UP: 'core/signup-wizard-step-sign-up.html',
    }

    form_list = (
        (STEP_START, forms.NoOperationForm),
        (STEP_WHAT_SELLING, forms.WhatAreYouSellingForm),
        (STEP_PRODUCT_SEARCH, forms.ProductSearchForm),
        (STEP_SIGN_UP, forms.NoOperationForm),
    )


class CompanyNameFormView(GA360Mixin, FormView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='MagnaPage',
            business_unit='MagnaUnit',
            site_section='signup-company-name',
        )

    template_name = 'core/company-name-form.html'
    form_class = forms.CompanyNameForm

    def get_success_url(self):
        return self.request.GET.get('next', cms_slugs.DASHBOARD_URL)

    def form_valid(self, form):
        helpers.update_company_profile(sso_session_id=self.request.user.session_id, data=form.cleaned_data)
        return super().form_valid(form)


class ContactUsHelpFormView(PageTitleMixin, FormView):
    form_class = forms.ContactUsHelpForm
    template_name = 'core/contact-us-help-form.html'
    success_url = reverse_lazy('core:contact-us-success')
    title = 'Contact us'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            form_kwargs['initial'] = {
                'email': self.request.user.email,
                'given_name': self.request.user.first_name,
                'family_name': self.request.user.last_name,
            }
        return form_kwargs

    def send_support_message(self, form):
        location = helpers.get_location(self.request)
        sender = Sender(
            email_address=form.cleaned_data['email'],
            country_code=location.get('country') if location else None,
            ip_address=helpers.get_sender_ip_address(self.request),
        )
        response = form.save(
            template_id=settings.CONTACTUS_ENQURIES_SUPPORT_TEMPLATE_ID,
            email_address=settings.GREAT_SUPPORT_EMAIL,
            form_url=self.request.get_full_path(),
            sender=sender,
        )
        response.raise_for_status()

    def send_user_message(self, form):
        # no need to set `sender` as this is just a confirmation email.
        response = form.save(
            template_id=settings.CONTACTUS_ENQURIES_CONFIRMATION_TEMPLATE_ID,
            email_address=form.cleaned_data['email'],
            form_url=self.request.get_full_path(),
        )
        response.raise_for_status()

    def form_valid(self, form):
        self.send_support_message(form)
        self.send_user_message(form)
        return super().form_valid(form)


class ContactUsHelpSuccessView(TemplateView):
    template_name = 'core/contact-us-help-form-success.html'


class ServiceNoLongerAvailableView(TemplateView):
    template_name = 'domestic/service_no_longer_available.html'

    def get_context_data(self, **kwargs):
        advice_page_slug = 'advice'

        return super().get_context_data(
            **kwargs, listing_page=TopicLandingPage.objects.filter(slug=advice_page_slug).first()
        )


class QuerystringRedirectView(RedirectView):
    query_string = True


class TranslationRedirectView(RedirectView):
    language = None
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL redirect
        """
        url = super().get_redirect_url(*args, **kwargs)

        if self.language:
            # Append 'lang' to query params
            if self.request.META.get('QUERY_STRING'):
                concatenation_character = '&'
            # Add 'lang' query param
            else:
                concatenation_character = '?'

            url = '{arg1}{arg2}lang={arg3}'.format(arg1=url, arg2=concatenation_character, arg3=self.language)

        return url


class OpportunitiesRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        redirect_url = '{export_opportunities_url}{slug}/'.format(
            export_opportunities_url=('/export-opportunities/'), slug=kwargs.get('slug', '')
        )

        query_string = self.request.META.get('QUERY_STRING')
        if query_string:
            redirect_url = '{redirect_url}?{query_string}'.format(redirect_url=redirect_url, query_string=query_string)

        return redirect_url


class CookiePreferencesPageView(TemplateView):
    # NB: template currently bears the ex-V1 styling, so comes from great-cms/domestic/templates/domestic/
    template_name = 'domestic/cookie-preferences.html'


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        base_url = settings.BASE_URL
        if base_url[-1] == '/':
            base_url = base_url[:-1]

        return super().get_context_data(
            **kwargs,
            base_url=base_url,
        )


def serve_subtitles(request, great_media_id, language):
    """Subtitles are stored along with the core.models.GreatMedia instance
    but they need to be served via their own dedicated URL.
    """

    video = get_object_or_404(GreatMedia, id=great_media_id)

    # See if there's a subtitle field for the appropriate languages
    field_name = f'subtitles_{language}'
    subtitles = getattr(video, field_name, None)
    if not bool(subtitles):
        raise Http404()

    response = HttpResponse(subtitles, content_type='text/vtt')
    return response


class CMSPagesSitemap(WagtailSitemap):
    """Extend the default Wagtail sitemap generator to skip over pages
    which use our custom authentication-required mixin.
    """

    def items(self) -> list:
        items_qs = super().items()
        # Unfortunately we have to do some filtering in code, not at the DB.
        # It's fine for the return value to be an iterable, not a QuerySet:
        # https://docs.djangoproject.com/en/3.2/ref/contrib/sitemaps/#sitemap-class-reference

        items = [instance for instance in items_qs if AuthenticatedUserRequired not in instance.__class__.mro()]

        return items


class StaticViewSitemap(DjangoSitemap):
    """A manually curated section of the sitemap, focused
    on Django-rendered views we want search engines to know about"""

    changefreq = 'daily'

    CONTACT_PAGE_PLACEHOLDER = 'CONTACT_PAGE_PLACEHOLDER'

    def items(self):
        # At the moment, these are deliberately only for unauthenticated pages.
        url_names = [
            # TODO: replace pre-resolved URLs, above, with the proper contact view URL names
            # when they have been ported from V1 into V2
            '/contact/',
            '/contact/events/',
            '/contact/defence-and-security-organisation/',
            '/contact/export-advice/',
            '/contact/feedback/',
            '/contact/domestic/',
            '/contact/domestic/enquiries/',
            '/contact/international/',
            '/contact/selling-online-overseas/',
            '/contact/selling-online-overseas/organisation/',
            '/contact/office-finder/',
            # These were removed from the V1 sitemap because the pages were 404ing anyway because
            # FEATURE_EXPORTING_TO_UK_ON_ENABLED was not set on production any more, so the views
            # ExportingToUKDERAFormView, ExportingToUKBEISFormView and ExportingToUKFormView have
            # NOT YET been ported to Great V2
            # '/contact/department-for-business-energy-and-industrial-strategy/',
            # '/contact/department-for-environment-food-and-rural-affairs/',
            # '/contact/exporting-to-the-uk/',
            # '/contact/exporting-to-the-uk/import-controls/',
            # '/contact/exporting-to-the-uk/other/',
            # '/contact/exporting-to-the-uk/trade-with-uk-app/',
            # The following are all auto-generated from the urlconf
            'core:cookie-preferences',
            'core:login',
            'core:signup',
            'core:robots',
            'domestic:get-finance',
            'domestic:uk-export-finance-lead-generation-form',  # See location(), below
            'domestic:project-finance',
            'domestic:how-we-assess-your-project',
            'domestic:what-we-offer-you',
            'domestic:country-cover',
            'domestic:uk-export-contact',
            'domestic:brexit-contact-form',
            'domestic:market-access',
            'domestic:report-ma-barrier',  # See location(), below
            'search:search',
            'search:feedback',
        ]
        return url_names

    def changefreq(self, item):
        # The Django-rendered pages don't change very often and we can always request
        # a re-crawl if we have something we edit that we want to get out there ASAP.
        # 'Monthly' seems like a reasonable middle ground, even though it might not be
        # respected by search engines anyway
        return 'monthly'

    def location(self, item):
        if item.startswith('/'):
            return item
        elif item == 'domestic:uk-export-finance-lead-generation-form':
            return reverse(item, kwargs={'step': 'contact'})
        elif item == 'domestic:report-ma-barrier':
            return reverse(item, kwargs={'step': 'about'})
        return reverse(item)
