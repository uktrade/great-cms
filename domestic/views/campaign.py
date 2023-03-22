from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
<<<<<<< HEAD
from django.urls import reverse_lazy
<<<<<<< HEAD

from contact.views import BaseNotifyUserFormView
=======
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from contact.views import BaseNotifyFormView
from core import mixins
>>>>>>> f8080801a (saving changes)
=======
from contact.views import BaseNotifyUserFormView
>>>>>>> 1bd781c15 (forms now working)
from core.datastructures import NotifySettings
from domestic.forms import CampaignLongForm, CampaignShortForm
from domestic.models import ArticlePage

<<<<<<< HEAD
<<<<<<< HEAD

class CampaignView(BaseNotifyUserFormView):
    def setup(self, request, *args, **kwargs):
=======

class CampaignView(BaseNotifyUserFormView):
    def setup(self, request, *args, **kwargs):

>>>>>>> 1bd781c15 (forms now working)
        page_slug = kwargs['page_slug']
        self.form_success = True if 'form_success' in kwargs else False

        def get_current_page():
            try:
                return ArticlePage.objects.live().get(slug=page_slug)
            except ObjectDoesNotExist:
                return None

        def get_form_value(page):
            values = [block.value for block in page.article_body if block.block_type == 'form']
            if len(values) > 0:
                return values[0]
            else:
                return None

        self.success_url = reverse_lazy('domestic:campaigns', kwargs={'page_slug': page_slug, 'form_success': 1})
        self.current_page = get_current_page()
        self.form_config = get_form_value(self.current_page) if self.current_page else None
        self.form_type = self.form_config['type'] if self.form_config else None
        self.email_title = self.form_config['email_title'] if self.form_type else None
        self.email_body = self.form_config['email_body'] if self.form_type else None
        self.email_subject = self.form_config['email_subject'] if self.form_type else None
        self.template_name = 'domestic/article_page.html'
        self.notify_settings = NotifySettings(
<<<<<<< HEAD
            user_template=settings.CAMPAIGN_USER_NOTIFY_TEMPLATE_ID,
        )
=======
        user_template=settings.CAMPAIGN_USER_NOTIFY_TEMPLATE_ID,
    )
>>>>>>> 1bd781c15 (forms now working)
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
<<<<<<< HEAD

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, page=self.current_page if self.current_page else None, form_success=self.form_success
        )
=======

class CampaignView(BaseNotifyFormView):
    template_name = 'domestic/article_page.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    notify_settings = NotifySettings(
        user_template=settings.SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID,
    )

    def get_current_page(self):
        try:
            return ArticlePage.objects.live().get(slug=self.kwargs['page_slug'])
        except ObjectDoesNotExist:
            return None

    def get_sectors(self):
        current_page = self.get_current_page()
        if current_page:
            return ArticlePage.get_sector_choices(current_page, self.request)
        else:
            return []

    def get_form_value(self, ArticlePage):
        values = [block.value for block in ArticlePage.article_body if block.block_type == 'form']
        if len(values) > 0:
            return values[0]
        else:
            return None

    def get_form(self):
        page = self.get_current_page()
        if page:
            form_type = self.get_form_value(page)
            if form_type == 'Short':
                return CampaignShortForm()
            elif form_type == 'Long':
                sector_choices = self.get_sectors()
                return CampaignLongForm(sector_choices)
                pass
        return None

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, page=self.get_current_page() if self.get_current_page() else None)
>>>>>>> f8080801a (saving changes)
=======

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, page=self.current_page if self.current_page else None,
                                        form_success=self.form_success)
>>>>>>> 1bd781c15 (forms now working)
