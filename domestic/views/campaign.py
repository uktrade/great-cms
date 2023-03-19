from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from contact.views import BaseNotifyFormView
from core.datastructures import NotifySettings
from domestic.forms import CampaignLongForm, CampaignShortForm
from domestic.models import ArticlePage
from contact import constants, forms as contact_forms, helpers
from django.shortcuts import render
class CampaignView(BaseNotifyFormView):
    

    def setup(self, request, *args, **kwargs):
        page_slug =  kwargs['page_slug']
        self.success_url = reverse_lazy('domestic:campaigns', kwargs = {'page_slug': page_slug})
        return super().setup(request, *args, **kwargs)

    template_name = 'domestic/article_page.html'
    notify_settings = NotifySettings(
        agent_template=settings.UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.UKEF_CONTACT_AGENT_EMAIL_ADDRESS,
        user_template=settings.UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID,
    )
        
    def get_current_page(self):
        try:
            return ArticlePage.objects.live().get(slug=self.kwargs['page_slug'])
        except ObjectDoesNotExist:
            return None

    def get_form_value(self, ArticlePage):
        values = [block.value for block in ArticlePage.article_body if block.block_type == 'form']
        if len(values) > 0:
            return values[0]
        else:                                                                                                                                                                       
            return None
        
    def get_form_class(self):  
        page = self.get_current_page()
        if page:
            form_type = self.get_form_value(page)
            if form_type == 'Short':
                return CampaignShortForm
            elif form_type == 'Long':
                return CampaignLongForm      
        else:
            return None 

        
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, page=self.get_current_page() if self.get_current_page() else None)
    