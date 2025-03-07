import logging
from django.conf import settings
from django.utils import translation
import requests
from great_components import helpers, forms
import uuid

logger = logging.getLogger(__name__)


class EnableTranslationsMixin:
    template_name_bidi = None
    language_form_class = forms.LanguageForm

    def __init__(self, *args, **kwargs):
        dependency = 'great_components.middleware.ForceDefaultLocale'
        if getattr(settings, 'MIDDLEWARE', []):
            assert dependency in settings.MIDDLEWARE
        else:
            assert dependency in settings.MIDDLEWARE_CLASSES
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        translation.activate(request.LANGUAGE_CODE)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['LANGUAGE_BIDI'] = translation.get_language_bidi()
        language_form_kwargs = self.get_language_form_kwargs()

        context['language_switcher'] = {
            'show': True,
            'form': self.language_form_class(**language_form_kwargs)
        }
        return context

    def get_language_form_kwargs(self, **kwargs):
        return {
            'initial': forms.get_language_form_initial_data(),
            **kwargs,
        }


class CMSLanguageSwitcherMixin:

    def dispatch(self, request, *args, **kwargs):
        translation.activate(request.LANGUAGE_CODE)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        form = forms.LanguageForm(
            initial={'lang': translation.get_language()},
            language_choices=self.page['meta']['languages']
        )
        show_language_switcher = (
            len(self.page['meta']['languages']) > 1 and
            form.is_language_available(translation.get_language())
        )
        return super().get_context_data(
            language_switcher={'form': form, 'show': show_language_switcher},
            *args,
            **kwargs
        )


class GA360Mixin:
    def __init__(self, *args, **kwargs):
        self.ga360_payload = {}
        super().__init__(*args, **kwargs)

    def set_ga360_payload(self, page_id, business_unit, site_section, site_subsection=None, referer_url=None):
        self.ga360_payload['page_id'] = page_id
        self.ga360_payload['business_unit'] = business_unit
        self.ga360_payload['site_section'] = site_section
        if site_subsection:
            self.ga360_payload['site_subsection'] = site_subsection
        if referer_url:
            self.ga360_payload['referer_url'] = referer_url

    def __send_to_ga4(self):
        logger.info('Sending to Google Analytics 4 (GA4)')
        req = requests.post(
            settings.GA4_API_URL,
            params={
                'api_secret': settings.GA4_API_SECRET,
                'measurement_id': settings.GA4_MEASUREMENT_ID,
            },
            json={
                'client_id': str(uuid.uuid4()),
                'events': [{
                    'name': 'page_view',
                    'params': {
                        'page_id': self.ga360_payload.get('page_id'),
                        'business_unit': self.ga360_payload.get('business_unit'),
                        'site_section': self.ga360_payload.get('site_section'),
                        'site_subsection': self.ga360_payload.get('site_subsection'),
                        'site_language': self.ga360_payload.get('site_language'),
                    }
                }],
            },
        )
        logger.info('Request status code %s', req.status_code)

    def get_context_data(self, *args, **kwargs):
        user = helpers.get_user(self.request)
        is_logged_in = helpers.get_is_authenticated(self.request)
        self.ga360_payload['login_status'] = is_logged_in
        self.ga360_payload['user_id'] = user.hashed_uuid if (is_logged_in and not user.is_superuser) else None
        self.ga360_payload['site_language'] = translation.get_language()
        self.__send_to_ga4()
        return super().get_context_data(ga360=self.ga360_payload, *args, **kwargs)
