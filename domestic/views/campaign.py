from babel import Locale as BabelLocale
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import get_language
from wagtail.models import Locale, Site

from contact.views import BaseNotifyUserFormView
from core.context_processors import microsite_footer, microsite_header
from core.datastructures import NotifySettings
from core.helpers import get_location
from core.models import MicrositePage
from domestic.forms import CampaignLongForm, CampaignShortForm
from domestic.models import ArticlePage


def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    """Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    """
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        return f'{base_url}?{urlencode(query_kwargs)}'
    return base_url


class CampaignView(BaseNotifyUserFormView):
    # overwite these variables to customize
    success_url_path = 'domestic:campaigns'
    page_class = ArticlePage
    template_name = 'domestic/article_page.html'
    streamfield_name = 'article_body'
    UK_COUNTRY_CODE = 'GB'
    notify_settings = NotifySettings(
        user_template=settings.CAMPAIGN_USER_NOTIFY_TEMPLATE_ID,
    )

    def get_current_page(self, request=None):
        if self.page_slug is None:
            return None
        try:
            current_language_code = get_language()
            current_locale = Locale.objects.get(language_code=current_language_code)
        except ObjectDoesNotExist:
            from config.settings import LANGUAGE_CODE

            current_locale = Locale.objects.get(language_code=LANGUAGE_CODE)
        return self.get_correct_page(current_locale, request)

    def get_correct_page(self, current_locale, request=None):
        if request:
            site = Site.find_for_request(request)
            translated_root = site.root_page.get_translation_or_none(current_locale)
            if not translated_root:
                translated_root = site.root_page
            pages = self.page_class.objects.live().descendant_of(translated_root)
            if pages.filter(slug=self.page_slug).count() > 0:
                if (
                    pages.filter(slug=self.page_slug, locale_id=current_locale, url_path__endswith=self.path).count()
                    == 1  # noqa: W503
                ):
                    return pages.get(slug=self.page_slug, locale_id=current_locale, url_path__endswith=self.path)
                else:
                    from config.settings import LANGUAGE_CODE

                    default_locale = Locale.objects.get(language_code=LANGUAGE_CODE)
                    if (
                        pages.filter(
                            slug=self.page_slug, locale_id=default_locale, url_path__endswith=self.path
                        ).count()
                        == 1
                    ):
                        return pages.get(slug=self.page_slug, locale_id=default_locale, url_path__endswith=self.path)
                    else:
                        return pages.filter(slug=self.page_slug, url_path__endswith=self.path).order_by('-path').first()

    def get_form_value(self):
        values = [
            block.value for block in getattr(self.current_page, self.streamfield_name) if block.block_type == 'form'
        ]
        if len(values) > 0:
            return values[0]
        else:
            return None

    def get_success_url(self):
        return reverse_querystring(
            self.success_url_path, kwargs={'page_slug': self.page_slug}, query_kwargs={'form_success': True}
        )

    def get_language_display_name(self, language_code):
        locale = BabelLocale.parse(language_code, sep='-')
        display_name = locale.get_display_name()
        return display_name

    def get_languages(self):
        def modify_language_display_names(display_name):
            strings_to_replace = {'(United Kingdom)'}
            for string in strings_to_replace:
                display_name = display_name.replace(string, '')
            return display_name

        rtl_languages = set()
        rtl_languages.add('ar')

        current_language_code = get_language()

        page_locales = Locale.objects.filter(
            id__in=self.page_class.objects.live()
            .filter(url_path__contains=self.path)
            .values_list('locale_id', flat=True)
        )

        return {
            'available_languages': [
                {
                    'language_code': locale.language_code,
                    'display_name': modify_language_display_names(self.get_language_display_name(locale.language_code)),
                    'is_rtl_language': locale.language_code in rtl_languages,
                }
                for locale in page_locales
            ],
            'current_language': current_language_code,
        }

    def _get_request_location_link(self):
        if not self.location or self.location['country'] == self.UK_COUNTRY_CODE:
            return '/'
        else:
            return '/internatonal/'

    def setup(self, request, *args, **kwargs):
        self.page_slug = kwargs['page_slug'] if 'page_slug' in kwargs else None
        self.form_success = True if 'form_success=True' in request.get_full_path() else False
        self.success_url = self.get_success_url()
        self.path = request.path
        self.request = request
        self.current_page = self.get_current_page(request)
        self.available_languages = self.get_languages()['available_languages'] if self.current_page else None
        self.current_language = self.get_languages()['current_language'] if self.current_page else None
        self.form_config = self.get_form_value() if self.current_page else None
        self.form_type = self.form_config['type'] if self.form_config else None
        self.email_title = self.form_config['email_title'] if self.form_type else None
        self.email_body = self.form_config['email_body'] if self.form_type else None
        self.email_subject = self.form_config['email_subject'] if self.form_type else None
        self.location = get_location(request)
        return super().setup(request, *args, **kwargs)

    def get_form_class(self):
        if self.form_type == 'Short':
            return CampaignShortForm
        elif self.form_type == 'Long':
            return CampaignLongForm
        else:
            return None

    def form_valid(self, form):
        form.cleaned_data['email_title'] = self.email_title
        form.cleaned_data['email_body'] = self.email_body
        form.cleaned_data['email_subject'] = self.email_subject
        self.send_user_message(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        if not self.form_type:
            kwargs['form'] = None
        if not self.current_page:
            raise Http404
        page = self.current_page
        include_link_to_great = page.get_include_link_to_great() if hasattr(page, 'get_include_link_to_great') else ''
        use_domestic_logo = page.get_use_domestic_header_logo() if hasattr(page, 'get_use_domestic_header_logo') else ''
        site_title = page.get_site_title() if hasattr(page, 'get_site_title') else ''
        menu_items = page.get_menu_items(self.request) if hasattr(page, 'get_menu_items') else ''
        bgs_menu_items = page.get_bgs_menu_items(self.request) if hasattr(page, 'get_bgs_menu_items') else ''
        site_href = (
            page.get_bgs_menu_items(self.request)[0]['href']
            if hasattr(page, 'get_bgs_menu_items') and page.get_bgs_menu_items(self.request)
            else ''
        )
        great_logo_href = (
            page.get_menu_items(self.request)[0]['href']
            if hasattr(page, 'get_menu_items') and page.get_menu_items(self.request)
            else ''
        )
        microsite_context = microsite_header(self.request)
        microsite_context['include_link_to_great'] = include_link_to_great
        microsite_context['use_domestic_logo'] = use_domestic_logo
        microsite_context['site_title'] = site_title
        microsite_context['subnavItemsList'] = menu_items
        microsite_context['bgsSubnavItemsList'] = bgs_menu_items
        microsite_context['siteHref'] = site_href
        microsite_context['great_logo_href'] = great_logo_href

        microsite_context['microsite_footer_context'] = microsite_footer(self.request)
        kwargs.update(microsite_context)

        return super().get_context_data(
            **kwargs,
            page=self.current_page,
            form_success=self.form_success,
            available_languages=self.available_languages,
            current_language=self.current_language,
            campaign_site_page=True,
            campaign_site_page_link=self._get_request_location_link(),
        )


class MicrositeView(CampaignView):
    success_url_path = '?form_success=True'
    page_class = MicrositePage
    template_name = '../../core/templates/microsites/micro_site_page.html'
    streamfield_name = 'page_body'

    def get_success_url(self):
        self.success_url_path += f'&lang={get_language()}'
