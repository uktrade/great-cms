from directory_forms_api_client.actions import PardotAction
from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from contact.views import BaseNotifyFormView
from core import mixins
from core.datastructures import NotifySettings
from domestic.forms import (
    CampaignLongForm,
    CampaignShortForm
)
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from domestic.models import ArticlePage

class CampaignView(BaseNotifyFormView):
    template_name = 'domestic/article_page.html'
    success_url = reverse_lazy('contact:contact-us-domestic-success')
    
    def get_form_value(self, ArticlePage):
        values =  [block.value for block in ArticlePage.article_body if block.block_type == 'form']
        if len(values) > 0:
            return values[0]
        else:
            return None
    
    def get_form(self):
        try:
            page = ArticlePage.objects.live().get(slug=self.kwargs['page_slug']) 
            form_type = self.get_form_value(page)
            if form_type == 'Short':
                return CampaignShortForm()
            elif form_type == 'Long':
                return CampaignLongForm()
            return None
        except ObjectDoesNotExist:
            return None
    
    def get_context_data(self, **kwargs):
        form = self.get_form()
        return super().get_context_data(
            **kwargs,
            form = form,
        )
        

        
    
   

