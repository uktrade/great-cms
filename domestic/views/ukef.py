from directory_forms_api_client.actions import PardotAction
from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from contact.views import BaseNotifyFormView
from core import mixins
from core.datastructures import NotifySettings
from domestic.forms import (
    CompanyDetailsForm,
    HelpForm,
    PersonalDetailsForm,
    UKEFContactForm,
)


class BespokeBreadcrumbMixin(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bespoke_breadcrumbs = [
            {'title': 'UKEF', 'url': reverse('domestic:get-finance')},
            {'title': 'Project Finance', 'url': reverse('domestic:project-finance')},
        ]
        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        return ctx


class UKEFHomeView(TemplateView):
    template_name = 'domestic/ukef/home_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['trade_finance_bullets'] = [
            'working capital support',
            'bond support',
            'credit insurance',
        ]
        context['project_finance_bullets'] = [
            'UKEF buyer credit guarantees',
            'direct lending',
            'credit and bond insurance',
        ]
        return context


class UKEFProjectFinanceView(TemplateView):
    template_name = 'domestic/ukef/project_finance.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bespoke_breadcrumbs = [
            {'title': 'UKEF', 'url': reverse('domestic:get-finance')},
        ]
        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        return ctx


class UKEFHowWeAssessView(BespokeBreadcrumbMixin, TemplateView):
    template_name = 'domestic/ukef/how_we_assess.html'


class UKEFWhatWeOfferView(BespokeBreadcrumbMixin, TemplateView):
    template_name = 'domestic/ukef/what_we_offer.html'


class UKEFCountryCoverView(BespokeBreadcrumbMixin, TemplateView):
    template_name = 'domestic/ukef/country_cover.html'


class ContactView(BespokeBreadcrumbMixin, BaseNotifyFormView):
    template_name = 'domestic/ukef/contact_form.html'
    form_class = UKEFContactForm
    success_url = reverse_lazy('domestic:uk-export-contact-success')
    notify_settings = NotifySettings(
        agent_template=settings.UKEF_CONTACT_AGENT_NOTIFY_TEMPLATE_ID,
        agent_email=settings.UKEF_CONTACT_AGENT_EMAIL_ADDRESS,
        user_template=settings.UKEF_CONTACT_USER_NOTIFY_TEMPLATE_ID,
    )

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        self.request.session['user_email'] = user_email
        return super().form_valid(form)


class SuccessPageView(BespokeBreadcrumbMixin, TemplateView):
    template_name = 'domestic/ukef/contact_form_success.html'

    def get(self, *args, **kwargs):
        if not self.request.session.get('user_email'):
            return HttpResponseRedirect(reverse_lazy('domestic:uk-export-contact'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_email'] = self.request.session.get('user_email')
        bespoke_breadcrumbs = context['bespoke_breadcrumbs']
        bespoke_breadcrumbs.append({'title': 'Get in touch', 'url': reverse('domestic:uk-export-contact')})
        context['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        return context


class GetFinanceLeadGenerationFormView(
    mixins.PrepopulateFormMixin,
    mixins.PreventCaptchaRevalidationMixin,
    NamedUrlSessionWizardView,
):
    success_url = reverse_lazy(
        'domestic:uk-export-finance-lead-generation-form-success',
    )

    PERSONAL_DETAILS = 'your-details'
    COMPANY_DETAILS = 'company-details'
    HELP = 'help'

    form_list = (
        (PERSONAL_DETAILS, PersonalDetailsForm),
        (COMPANY_DETAILS, CompanyDetailsForm),
        (HELP, HelpForm),
    )
    templates = {
        PERSONAL_DETAILS: 'domestic/finance/lead_generation_form/step-personal.html',
        COMPANY_DETAILS: 'domestic/finance/lead_generation_form/step-company.html',
        HELP: 'domestic/finance/lead_generation_form/step-help.html',
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bespoke_breadcrumbs = [
            {'title': 'UKEF', 'url': reverse('domestic:get-finance')},
            {'title': 'Trade Finance', 'url': '/trade-finance'},
        ]
        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs

        return ctx

    def get_form_kwargs(self, *args, **kwargs):
        # skipping `PrepopulateFormMixin.get_form_kwargs`
        return super(mixins.PrepopulateFormMixin, self).get_form_kwargs(*args, **kwargs)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if self.request.user.is_authenticated:
            if step == self.PERSONAL_DETAILS and self.request.user.company:
                initial.update(
                    {
                        'email': self.request.user.email,
                        'phone': getattr(self.request.user.company, 'mobile_number', ''),
                        'firstname': self.guess_given_name,  # /PS-IGNORE
                        'lastname': self.guess_family_name,  # /PS-IGNORE
                    }
                )
            elif step == self.COMPANY_DETAILS and self.request.user.company:
                company = self.request.user.company

                _sectors = getattr(company, 'sectors', [])
                _industry = _sectors[0] if _sectors else None
                initial.update(
                    {
                        'not_companies_house': False,
                        'company_number': getattr(company, 'number', ''),
                        'trading_name': getattr(company, 'name', ''),
                        'address_line_one': getattr(company, 'address_line_1', ''),
                        'address_line_two': getattr(company, 'address_line_2', ''),
                        'address_town_city': getattr(company, 'locality', ''),
                        'address_post_code': getattr(company, 'postal_code', ''),
                        'industry': _industry,
                    }
                )
        return initial

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = self.serialize_form_list(form_list)
        sender = Sender(email_address=form_data['email'], country_code=None)
        action = PardotAction(
            pardot_url=settings.UKEF_FORM_SUBMIT_TRACKER_URL,
            form_url=reverse('domestic:uk-export-finance-lead-generation-form', kwargs={'step': self.PERSONAL_DETAILS}),
            sender=sender,
        )
        response = action.save(form_data)
        response.raise_for_status()
        return redirect(self.success_url)

    @staticmethod
    def serialize_form_list(form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        return data
