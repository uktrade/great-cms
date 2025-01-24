import abc
import json
import logging
import pickle
from datetime import datetime

from directory_forms_api_client import actions
from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.contrib.sitemaps import Sitemap as DjangoSitemap
from django.core.files.storage import default_storage
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from django.views.generic.base import RedirectView, View
from formtools.wizard.views import NamedUrlSessionWizardView
from great_components.mixins import GA360Mixin  # /PS-IGNORE
from rest_framework import generics
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from storages.backends.s3boto3 import S3Boto3Storage
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap
from wagtail.documents.models import Document
from wagtail.images import get_image_model
from wagtail.images.views import chooser
from wagtail.images.views.chooser import (
    ImageChooserViewSet,
    ImageChosenResponseMixin,
    ImageCreationFormMixin,
    ImageInsertionForm,
    ImageUploadViewMixin,
)
from wagtailcache.cache import WagtailCacheMixin, nocache_page

from core import cms_slugs, forms, helpers, serializers
from core.constants import PRODUCT_MARKET_DATA
from core.mixins import (
    AuthenticatedUserRequired,
    GuidedJourneyMixin,
    HCSATMixin,
    PageTitleMixin,
)
from core.models import GreatMedia
from core.pingdom.services import health_check_services
from directory_constants import choices
from domestic.helpers import (
    get_market_widget_data_helper,
    get_sector_widget_data_helper,
)
from domestic.models import DomesticDashboard, TopicLandingPage
from export_academy.models import Event
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


class ArticleView(GA360Mixin, FormView):  # /PS-IGNORE
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
        topic_name = self.kwargs['topic']
        chapter_name = self.kwargs['chapter']

        bespoke_breadcrumbs = [
            {'title': 'Dashboard', 'url': '/dashboard/'},
            {'title': topic_name, 'url': 'https://www.example.com'},
            {'title': chapter_name, 'url': 'https://www.example.com'},
        ]
        return super().get_context_data(
            topic_name=self.kwargs['topic'],
            chapter_name=self.kwargs['chapter'],
            article_name=self.kwargs['article'],
            country_choices=[{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
            bespoke_breadcrumbs=bespoke_breadcrumbs,
        )


class LoginView(GA360Mixin, PageTitleMixin, TemplateView):  # /PS-IGNORE
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


class SignupView(GA360Mixin, PageTitleMixin, TemplateView):  # /PS-IGNORE
    template_name = 'core/signup.html'
    title = 'Sign up'

    def get_context_data(self, **kwargs):
        referrer = self.request.META.get('HTTP_REFERER')
        self.set_ga360_payload(
            page_id='MagnaPage', business_unit='MagnaUnit', site_section='signup', referer_url=referrer
        )
        context = super().get_context_data(**kwargs)
        return context


class CompareCountriesView(
    WagtailCacheMixin, GA360Mixin, PageTitleMixin, HCSATMixin, TemplateView, FormView  # /PS-IGNORE
):

    cache_control = 'no-cache'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='TargetMarkets',
            business_unit='MagnaUnit',
            site_section='target markets',
        )
        self.hcsat_session_name = 'where_to_export_csat_id'

    template_name = 'core/compare_countries.html'
    title = 'Where to export'
    form_class = forms.HCSATForm
    hcsat_service_name = 'where_to_export'

    def get_context_data(self, **kwargs):
        dashboard = DomesticDashboard.objects.live().first()
        context = super().get_context_data(**kwargs)
        context['data_tabs_enabled'] = json.dumps(settings.FEATURE_COMPARE_MARKETS_TABS)
        context['max_compare_places_allowed'] = settings.MAX_COMPARE_PLACES_ALLOWED
        context['dashboard_components'] = dashboard.components if dashboard else None

        context = self.set_csat_and_stage(self.request, context, self.hcsat_service_name, form=self.form_class)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        return context

    def post(self, request, *args, **kwargs):
        form_class = self.form_class

        hcsat = self.get_hcsat(request, self.hcsat_service_name)
        post_data = self.request.POST

        if 'cancelButton' in post_data:
            """
            Redirect user if 'cancelButton' is found in the POST data
            """
            if hcsat:
                hcsat.stage = 2
                hcsat.save()
            return HttpResponseRedirect(self.get_success_url())

        form = form_class(post_data)

        if form.is_valid():
            if hcsat:
                form = form_class(post_data, instance=hcsat)
                form.is_valid()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        super().form_invalid(form)
        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse(form.errors, status=400)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        super().form_valid(form)
        js_enabled = False
        hcsat = form.save(commit=False)

        # js version handles form progression in js file, so keep on 0 for reloads
        if 'js_enabled' in self.request.get_full_path():
            hcsat.stage = 0
            js_enabled = True

        # if in second part of form (satisfaction=None) or not given in first part, persist existing satisfaction rating
        hcsat = self.persist_existing_satisfaction(self.request, self.hcsat_service_name, hcsat)

        # Apply data specific to this service
        hcsat.URL = reverse_lazy('core:compare-countries')
        hcsat.user_journey = 'ADD_PRODUCT'
        hcsat.session_key = self.request.session.session_key

        hcsat.save(js_enabled=js_enabled)

        self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse({'pk': hcsat.pk})
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('core:compare-countries')


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
    if '/international/' in request.path:
        return TemplateResponse(request=request, template='international/404.html', context={}, status=404)
    else:
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


class SignupForTailoredContentWizardView(GA360Mixin, AbstractSignupWizardView, NamedUrlSessionWizardView):  # /PS-IGNORE
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

    def get_context_data(self, **kwargs):
        if self.request.GET.get('next'):
            next_url = helpers.check_url_host_is_safelisted(self.request)
            return super().get_context_data(**kwargs, next_url=next_url)
        return super().get_context_data(**kwargs)


class SignupForExportPlanWizardView(GA360Mixin, AbstractSignupWizardView, NamedUrlSessionWizardView):  # /PS-IGNORE
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


class CompanyNameFormView(GA360Mixin, FormView):  # /PS-IGNORE
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


class PermanentQuerystringRedirectView(QuerystringRedirectView):
    permanent = True


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


class ItemsIterator:
    def __init__(self, items):
        self.items = items

    def iterator(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return ItemsIterator(self.items[key])


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

        return ItemsIterator(items)


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
            'domestic:market-access',
            'domestic:report-ma-barrier',  # See location(), below
            'search:search',
            'search:feedback',
        ]
        return url_names

    def changefreq(self, item):  # noqa: F811
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


class SignedURLView(GenericAPIView):
    storage: S3Boto3Storage = default_storage

    def post(self, request, *args, **kwargs):
        client = self.storage.connection.meta.client
        request_file_name = request.data.get('fileName', get_random_string(7))
        qualified_key = f'media/{request_file_name}'
        key = self.storage.get_available_name(qualified_key)

        url = client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.storage.bucket.name,
                'Key': key,
            },
            ExpiresIn=3600,
        )
        return Response({'url': url, 'key': key})


class AltImageUploadView(ImageUploadViewMixin, ImageCreationFormMixin, ImageChosenResponseMixin, View):
    """
    AltImageUploadView class created to override ImageUploadViewMixin
    This view is required to prevent the alt text of an Uploaded image being
    set to the Image file name, which is the default Wagtail behaviour, see
    https://github.com/wagtail/wagtail/issues/10800
    """

    def post(self, request):
        self.model = get_image_model()
        self.form = self.get_creation_form()

        if self.form.is_valid():
            image = self.save_form(self.form)

            duplicates = chooser.find_image_duplicates(
                image=image,
                user=request.user,
                permission_policy=chooser.permission_policy,
            )
            existing_image = duplicates.first()
            if existing_image:
                return self.render_duplicate_found_response(request, image, existing_image)

            if request.GET.get('select_format'):
                insertion_form = ImageInsertionForm(
                    initial={'alt_text': image.alt_text if image.alt_text else image.default_alt_text},
                    prefix='image-chooser-insertion',
                )
                return self.render_select_format_response(image, insertion_form)
            else:
                # not specifying a format; return the image details now
                return self.get_chosen_response(image)

        else:  # form is invalid
            return self.get_reshow_creation_form_response()


class AltImageChooserViewSet(ImageChooserViewSet):
    model = get_image_model()
    create_view_class = AltImageUploadView
    register_widget = True

    def on_register(self):
        return super().on_register()


class DesignSystemView(TemplateView):
    template_name = 'design-system/design-system.html'


class ProductMarketView(TemplateView):
    template_name = 'core/product-market.html'

    def get_context_data(self):
        countries_data = PRODUCT_MARKET_DATA
        country = countries_data.get(self.request.GET.get('market'))
        countries = [country['display_name'] for country in countries_data.values()]

        return super().get_context_data(
            countries=countries,
            country=country,
            product=self.request.GET.get('product'),
            market=self.request.GET.get('market'),
            is_market_lookup_state=not self.request.GET.get('market'),
            is_results_state=self.request.GET.get('product') and self.request.GET.get('market'),
        )

    def post(self, request, *args, **kwargs):
        product = request.POST.get('product-input')
        market = request.POST.get('market-input')
        no_market = request.GET.get('no_market')
        action = actions.SaveOnlyInDatabaseAction(
            full_name='Anonymous user',
            subject='Product and Market experiment',
            email_address='anonymous-user@test.com',  # /PS-IGNORE
            form_url=self.request.get_full_path(),
        )

        if product and not market:
            return redirect(reverse_lazy('core:product-market') + '?product=' + product)

        if no_market:
            data = {
                'product': request.POST.get('product'),
                'market': None,
                'userid': self.request.user.hashed_uuid if self.request.user.is_authenticated else None,
            }
            response = action.save(data)
            response.raise_for_status()

            return redirect('/markets')
        elif market:
            product = request.POST.get('product')
            data = {
                'product': product,
                'market': market,
                'userid': self.request.user.hashed_uuid if self.request.user.is_authenticated else None,
            }
            response = action.save(data)
            response.raise_for_status()

            return redirect(reverse_lazy('core:product-market') + '?product=' + product + '&market=' + market.lower())
        else:
            return redirect(reverse_lazy('core:product-market'))


HEALTH_CHECK_STATUS = 0
HEALTH_CHECK_EXCEPTION = 1


@method_decorator(nocache_page, name='get')
class PingDomView(TemplateView):
    template_name = 'directory_healthcheck/pingdom.xml'

    status = 'OK'

    def get(self, *args, **kwargs):
        checked = {}
        for service in health_check_services:
            checked[service.name] = service().check()

        if all(item[HEALTH_CHECK_STATUS] for item in checked.values()):
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': []}),
                status=200,
                content_type='text/xml',
            )
        else:
            self.status = 'FALSE'
            errors = []
            for service_result in filter(lambda x: x[HEALTH_CHECK_STATUS] is False, checked.values()):
                errors.append(service_result[HEALTH_CHECK_EXCEPTION])
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': errors}),
                status=500,
                content_type='text/xml',
            )


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(nocache_page, name='get')
class GuidedJourneyStep1View(GuidedJourneyMixin, FormView):
    form_class = forms.GuidedJourneyStep1Form
    template_name = 'domestic/contact/export-support/guided-journey/step-1.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            progress_position=1,
            sic_sector_data=helpers.get_sectors_and_sic_sectors_file(),
        )

    def get_success_url(self):
        is_goods_exporter = False
        is_service_exporter = False
        return_to_step = self.request.GET.get('return_to_step')
        commodity_lookup_results = None
        commodity_length = 0

        if self.request.session.get('guided_journey_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('guided_journey_data')))[0]

            is_service_exporter = form_data['exporter_type'] == 'service'
            is_goods_exporter = form_data['exporter_type'] == 'goods'

            if is_goods_exporter:
                commodity_lookup_results = helpers.product_picker(form_data.get('make_or_do_keyword'))['data']
                commodity_length = len(commodity_lookup_results)

        conditions = (
            (is_service_exporter and return_to_step, reverse_lazy(f'core:guided-journey-step-{return_to_step}')),
            (is_service_exporter, reverse_lazy('core:guided-journey-step-3')),
            (not is_goods_exporter and not is_service_exporter, reverse_lazy('core:guided-journey-step-3')),
            (return_to_step, reverse_lazy('core:guided-journey-step-2-edit') + f'?return_to_step={return_to_step}'),
        )

        for condition, url in conditions:
            if condition:
                return url

        if commodity_length == 1:
            commodity_name = ''
            hs_code = ''

            for item in commodity_lookup_results:
                commodity_name = item['attributes']['title']
                hs_code = item['attributes']['goods_nomenclature_item_id']

            form_data = ({**form_data, 'hs_code': hs_code, 'commodity_name': commodity_name},)
            form_data = pickle.dumps(form_data).hex()
            self.request.session['guided_journey_data'] = form_data

            return reverse_lazy('core:guided-journey-step-3')

        return reverse_lazy('core:guided-journey-step-2')

    def form_valid(self, form):
        if form.cleaned_data['exporter_type'] == 'service':
            form.cleaned_data['hs_code'] = ''
            form.cleaned_data['commodity_name'] = ''

        self.save_data(form)
        return super().form_valid(form)


@method_decorator(nocache_page, name='get')
class GuidedJourneyStep1GetView(View):
    def get(self, request):
        sector = request.GET.get('sector')
        make_or_do = request.GET.get('make_or_do')
        exporter_type = request.GET.get('exporter_type')
        sic_description = request.GET.get('sic_description')

        if sector and make_or_do and exporter_type and sic_description:
            form_data = (
                {
                    'sector': sector,
                    'make_or_do': make_or_do,
                    'exporter_type': exporter_type,
                    'sic_description': sic_description,
                },
            )
            form_data = pickle.dumps(form_data).hex()
            self.request.session['guided_journey_data'] = form_data

            if exporter_type == 'goods':
                return HttpResponseRedirect(reverse_lazy('core:guided-journey-step-2'))

            return HttpResponseRedirect(reverse_lazy('core:guided-journey-step-3'))

        return HttpResponseRedirect(reverse_lazy('core:guided-journey-step-1'))


@method_decorator(nocache_page, name='get')
class GuidedJourneyStep2View(GuidedJourneyMixin, FormView):
    form_class = forms.GuidedJourneyStep2Form
    template_name = 'domestic/contact/export-support/guided-journey/step-2.html'

    def get_context_data(self, **kwargs):
        form_data = {}
        show_results = False
        commodities = None

        def get_hmrc_tarriff_data(make_or_do_keyword):
            deserialised_data = helpers.product_picker(make_or_do_keyword)
            mapped_results = [
                {
                    'title': 'Please select...',
                    'hs_code': '',
                }
            ]
            for item in deserialised_data['data']:
                mapped_results.append(
                    {
                        'title': item['attributes']['title'],
                        'hs_code': item['attributes']['goods_nomenclature_item_id'],
                    }
                )
            return mapped_results

        if self.request.session.get('guided_journey_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('guided_journey_data')))[0]

            if form_data.get('is_keyword_match') == 'True' and form_data.get('make_or_do_keyword'):
                commodities = get_hmrc_tarriff_data(form_data.get('make_or_do_keyword'))

                if len(commodities) > 2:
                    show_results = True

            form_data = ({**form_data, 'hs_code': '', 'commodity_name': ''},)
            form_data = pickle.dumps(form_data).hex()
            self.request.session['guided_journey_data'] = form_data

        return super().get_context_data(
            **kwargs,
            progress_position=2,
            form_data=form_data,
            show_results=show_results,
            commodities=commodities,
        )

    def get_success_url(self):
        return_to_step = self.request.GET.get('return_to_step')

        if return_to_step:
            return reverse_lazy(f'core:guided-journey-step-{return_to_step}')

        return reverse_lazy('core:guided-journey-step-3')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


@method_decorator(nocache_page, name='get')
class GuidedJourneyStep3View(GuidedJourneyMixin, FormView):
    form_class = forms.GuidedJourneyStep3Form
    template_name = 'domestic/contact/export-support/guided-journey/step-3.html'

    def get_context_data(self, **kwargs):
        countries = helpers.get_markets_list()
        countries = [(country_code, country) for country_code, country in countries if country_code != 'GB']

        return super().get_context_data(
            **kwargs,
            progress_position=3,
            countries=countries,
        )

    def get_success_url(self):
        return_to_step = self.request.GET.get('return_to_step')

        if return_to_step:
            return reverse_lazy(f'core:guided-journey-step-{return_to_step}')

        return reverse_lazy('core:guided-journey-step-4')

    def form_valid(self, form):
        self.save_data(form)
        return super().form_valid(form)


@method_decorator(nocache_page, name='get')
class GuidedJourneyStep4View(GuidedJourneyMixin, TemplateView):
    template_name = 'domestic/contact/export-support/guided-journey/step-4.html'

    def get_context_data(self, **kwargs):
        categories = []
        countries = helpers.get_markets_list()
        country_code = ''
        restricted_markets = ['Ukraine', 'Russia', 'Belarus', 'Israel']
        is_restricted_market = False
        is_market_skipped = self.request.GET.get('is_market_skipped')
        trade_barrier_count = None
        ukea_events = None
        sector = None
        market_guide = None

        if self.request.session.get('guided_journey_data'):
            form_data = pickle.loads(bytes.fromhex(self.request.session.get('guided_journey_data')))[0]
            market = form_data.get('market')
            sector = form_data.get('sector')
            ukea_events = helpers.get_ukea_events(
                Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date').all(), market, sector
            )

            for code, name in countries:
                if name == market:
                    country_code = code

            if market:
                is_restricted_market = market in restricted_markets
                trade_barrier_count = helpers.get_trade_barrier_count(market, None)
                market_guide = get_market_widget_data_helper(market)
            elif sector:
                trade_barrier_count = helpers.get_trade_barrier_count(None, sector)

            categories = helpers.mapped_categories(form_data)

            action = actions.SaveOnlyInDatabaseAction(
                full_name='Anonymous user',
                subject='Guided Journey',
                email_address='anonymous-user@test.com',  # /PS-IGNORE
                form_url=self.request.get_full_path(),
            )

            data = {
                'sic_description': form_data.get('sic_description') if form_data.get('sic_description') else None,
                'sector': form_data.get('sector') if form_data.get('sector') else None,
                'exporter_type': form_data.get('exporter_type') if form_data.get('exporter_type') else None,
                'hs_code': form_data.get('hs_code') if form_data.get('hs_code') else None,
                'market': form_data.get('market') if form_data.get('market') else None,
                'commodity_name': form_data.get('commodity_name') if form_data.get('commodity_name') else None,
                'not_sure_where_to_export': (
                    form_data.get('not_sure_where_to_export') if form_data.get('not_sure_where_to_export') else None
                ),
                'market_not_listed': form_data.get('market_not_listed') if form_data.get('market_not_listed') else None,
            }
            response = action.save(data)
            response.raise_for_status()

        return super().get_context_data(
            **kwargs,
            progress_position=4,
            suggested_markets=get_sector_widget_data_helper(sector),
            is_restricted_market=is_restricted_market,
            is_market_skipped=is_market_skipped,
            country_code=country_code,
            categories=categories,
            trade_barrier_count=trade_barrier_count,
            ukea_events=ukea_events,
            market_guide=market_guide,
        )


class WagtailServeDocument(View):

    def get(self, request, document_title):
        try:
            document = Document.objects.get(title=document_title)
        except Document.DoesNotExist:
            return HttpResponseBadRequest(())
        else:
            return HttpResponseRedirect(redirect_to=document.file.url)
