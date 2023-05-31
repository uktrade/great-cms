from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import get_language
from wagtail.models import Locale

from config.settings import FEATURE_MICROSITE_ENABLE_EXPERIMENTAL_LANGUAGE
from contact.views import BaseNotifyUserFormView
from core.datastructures import NotifySettings
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
    notify_settings = NotifySettings(
        user_template=settings.CAMPAIGN_USER_NOTIFY_TEMPLATE_ID,
    )

    def get_current_page(self):
        if self.page_slug is None:
            return None
        try:
            if FEATURE_MICROSITE_ENABLE_EXPERIMENTAL_LANGUAGE:
                from config.settings import LANGUAGE_CODE

                current_language_code = get_language()
                current_locale = Locale.objects.get(language_code=current_language_code)

                if self.page_class.objects.live().filter(slug=self.page_slug).count() > 0:
                    if (
                        self.page_class.objects.live()
                        .filter(slug=self.page_slug, locale_id=current_locale, url_path__endswith=self.path)
                        .count()
                        == 1  # noqa: W503
                    ):
                        return self.page_class.objects.live().get(
                            slug=self.page_slug, locale_id=current_locale, url_path__endswith=self.path
                        )
                    else:
                        default_locale = Locale.objects.get(language_code=LANGUAGE_CODE)
                        return self.page_class.objects.live().get(
                            slug=self.page_slug, locale_id=default_locale, url_path__endswith=self.path
                        )

            return self.page_class.objects.live().get(slug=self.page_slug, url_path__endswith=self.path)

        except ObjectDoesNotExist:
            return None

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

    def setup(self, request, *args, **kwargs):
        self.page_slug = kwargs['page_slug'] if 'page_slug' in kwargs else None

        self.form_success = True if 'form_success=True' in request.get_full_path() else False

        self.success_url = self.get_success_url()
        self.path = request.path
        self.current_page = self.get_current_page()
        self.form_config = self.get_form_value() if self.current_page else None
        self.form_type = self.form_config['type'] if self.form_config else None
        self.email_title = self.form_config['email_title'] if self.form_type else None
        self.email_body = self.form_config['email_body'] if self.form_type else None
        self.email_subject = self.form_config['email_subject'] if self.form_type else None
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
        return super().get_context_data(
            **kwargs, page=self.current_page if self.current_page else None, form_success=self.form_success
        )


class MicrositeView(CampaignView):
    page_class = MicrositePage
    template_name = '../../core/templates/microsites/micro_site_page.html'
    streamfield_name = 'page_body'

    def get_success_url(self):
        query_params = {'form_success': True}

        if FEATURE_MICROSITE_ENABLE_EXPERIMENTAL_LANGUAGE:
            query_params['lang'] = get_language()

        return reverse_querystring('core:microsites', kwargs={'page_slug': self.page_slug}, query_kwargs=query_params)
