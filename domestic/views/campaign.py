from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy

from contact.views import BaseNotifyUserFormView
from core.datastructures import NotifySettings
from domestic.forms import CampaignLongForm, CampaignShortForm
from domestic.models import ArticlePage


class CampaignView(BaseNotifyUserFormView):
    def setup(self, request, *args, **kwargs):
        page_slug = kwargs['page_slug'] if 'page_slug' in kwargs else None
        print(kwargs)
        print(request)
        self.form_success = True if 'form_success' in kwargs else False

        def get_current_page():
            if page_slug is None:
                return None
            try:
                print(ArticlePage.objects.live())
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
            user_template=settings.CAMPAIGN_USER_NOTIFY_TEMPLATE_ID,
        )
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
        return super().get_context_data(
            **kwargs, page=self.current_page if self.current_page else None, form_success=self.form_success
        )
