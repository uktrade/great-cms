from directory_forms_api_client import actions
from directory_forms_api_client.helpers import Sender
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin  # /PS-IGNORE
from wagtailcache.cache import WagtailCacheMixin

from config import settings
from core.constants import HCSatStage
from core.forms import HCSATForm
from core.helpers import check_url_host_is_safelisted
from core.mixins import HCSATMixin
from international import forms


class ContactView(WagtailCacheMixin, GA360Mixin, FormView):  # /PS-IGNORE
    form_class = forms.ContactForm
    template_name = 'international/contact.html'
    subject = 'Great.gov.uk International contact form'

    cache_control = 'no-cache'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Great.gov.uk International',
            site_section='contact',
        )

    def get_back_url(self):
        back_url = '/'
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_success_url(self):
        success_url = reverse_lazy('international:contact-success')
        if self.request.GET.get('next'):
            success_url = success_url + '?next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            site='Business.gov.uk' if settings.FEATURE_DOMESTIC_GROWTH else 'great.gov.uk',
        )

    def submit_feedback(self, form):
        cleaned_data = form.cleaned_data
        is_human_submission = 'csrfmiddlewaretoken' not in cleaned_data

        # Return HttpResponseBadRequest() for all requests not made by a human
        if is_human_submission is False:
            return HttpResponseBadRequest()

        if self.request.GET.get('next'):
            cleaned_data['from_url'] = check_url_host_is_safelisted(self.request)

        sender = Sender(
            email_address=cleaned_data['email'],
            country_code=None,
        )

        action = actions.ZendeskAction(
            full_name=cleaned_data['full_name'],
            email_address=cleaned_data['email'],
            subject=self.subject,
            service_name='great',
            form_url=reverse('international:contact'),
            sender=sender,
        )

        response = action.save(cleaned_data)
        response.raise_for_status()

    def form_valid(self, form):
        self.submit_feedback(form)
        return super().form_valid(form)


class ContactSuccessView(WagtailCacheMixin, HCSATMixin, FormView, GA360Mixin, TemplateView):  # /PS-IGNORE
    template_name = 'international/contact_success.html'
    subject = 'Great.gov.uk International contact form success'
    hcsat_service_name = 'find_a_supplier'
    cache_control = 'no-cache'
    form_class = HCSATForm

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='Contact',
            business_unit='Great.gov.uk International',
            site_section='contact',
        )

    def get_success_url(self):
        success_url = reverse_lazy('international:contact-success')
        if self.request.GET.get('next'):
            success_url = success_url + '?next=' + check_url_host_is_safelisted(self.request)
        return success_url

    def get_back_url(self):
        back_url = '/international/'
        if self.request.GET.get('next'):
            back_url = check_url_host_is_safelisted(self.request)
        return back_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs,
            back_url=self.get_back_url(),
            site='Business.gov.uk' if settings.FEATURE_DOMESTIC_GROWTH else 'great.gov.uk',
        )
        context = self.set_csat_and_stage(self.request, context, self.hcsat_service_name, self.form_class)
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
                hcsat.stage = HCSatStage.COMPLETED.value
                hcsat.save()
            return HttpResponseRedirect(self.get_success_url())

        form = form_class(post_data)

        if form.is_valid():
            if 'buy-from-the-uk' in self.request.GET.get('next', ''):
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

        if 'js_enabled' in self.request.get_full_path():
            hcsat.stage = HCSatStage.NOT_STARTED.value
            js_enabled = True

        hcsat = self.persist_existing_satisfaction(self.request, self.hcsat_service_name, hcsat)

        # Apply data specific to this service
        hcsat.URL = '/international/buy-from-the-uk/'
        hcsat.user_journey = 'COMPANY_CONTACT'
        hcsat.session_key = self.request.session.session_key
        hcsat.save(js_enabled=js_enabled)

        self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse({'pk': hcsat.pk})
        return HttpResponseRedirect(self.get_success_url())
