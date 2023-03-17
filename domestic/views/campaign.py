from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from contact.views import BaseNotifyFormView
from core.datastructures import NotifySettings
from domestic.forms import CampaignLongForm, CampaignShortForm
from domestic.models import ArticlePage


class CampaignView(BaseNotifyFormView):
   
    template_name = 'domestic/article_page.html'
    success_url = reverse_lazy('contact:contact-free-trade-agreements-success')
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

    def get_form_context(self):
        page = self.get_current_page()
        if page:
            form_type = self.get_form_value(page)
            if form_type == 'Short':
                return CampaignShortForm()
            elif form_type == 'Long':
                sector_choices = self.get_sectors()
                return CampaignLongForm(sector_choices)       
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs, page=self.get_current_page() if self.get_current_page() else None)
        # context['form'] = self.get_form_context()   
        return context