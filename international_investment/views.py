from directory_forms_api_client import actions
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from great_components.mixins import GA360Mixin  # /PS-IGNORE

from config import settings
from international_investment.core.helpers import get_location_display
from international_investment.forms import (
    InvestmentContactForm,
    InvestmentEstimateForm,
    InvestmentFundForm,
    InvestmentTypesForm,
)
from international_online_offer.forms import SpendCurrencySelectForm


class InvestmentFundView(GA360Mixin, FormView):  # /PS-IGNORE
    form_class = InvestmentFundForm
    template_name = 'investment/investment_fund.html'
    success_url = reverse_lazy('international_investment:investment-types')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentFund',
            business_unit='Investment',
            site_section='investment-fund',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = '/international/investment/'
        return context

    def form_valid(self, form):
        if not self.request.session.get('triage_data'):
            self.request.session['triage_data'] = {}
        self.request.session['triage_data'] = {**self.request.session['triage_data'], **form.cleaned_data}
        return super().form_valid(form)

    def get_initial(self):
        return self.request.session.get('triage_data')


class InvestmentTypesView(GA360Mixin, FormView):  # /PS-IGNORE
    form_class = InvestmentTypesForm
    template_name = 'investment/investment_types.html'
    success_url = reverse_lazy('international_investment:investment-estimate')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentTypes',
            business_unit='Investment',
            site_section='investment-types',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('international_investment:investment-fund')
        return context

    def form_valid(self, form):
        if not self.request.session.get('triage_data'):
            self.request.session['triage_data'] = {}
        self.request.session['triage_data'] = {**self.request.session['triage_data'], **form.cleaned_data}
        return super().form_valid(form)

    def get_initial(self):
        return self.request.session.get('triage_data')


class InvestmentEstimateView(GA360Mixin, FormView):  # /PS-IGNORE
    form_class = InvestmentEstimateForm
    template_name = 'investment/investment_estimate.html'
    success_url = reverse_lazy('international_investment:investment-contact-details')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentEstimate',
            business_unit='Investment',
            site_section='investment-estimate',
        )

    def get_form_kwargs(self):
        kwargs = super(InvestmentEstimateView, self).get_form_kwargs()
        spend_currency = self.request.session.get('spend_currency')
        kwargs['spend_currency'] = spend_currency
        return kwargs

    def get_context_data(self, **kwargs):
        spend_currency_param = self.request.GET.get('spend_currency')
        if spend_currency_param:
            self.request.session['spend_currency'] = spend_currency_param

        return super().get_context_data(
            **kwargs,
            back_url=reverse_lazy('international_investment:investment-types'),
            spend_currency_form=SpendCurrencySelectForm(
                initial={'spend_currency': self.request.session.get('spend_currency')}
            ),
        )

    def form_valid(self, form):
        if not self.request.session.get('triage_data'):
            self.request.session['triage_data'] = {}
        self.request.session['triage_data'] = {**self.request.session['triage_data'], **form.cleaned_data}
        return super().form_valid(form)

    def get_initial(self):
        initial_data = self.request.session.get('triage_data')
        if self.request.session.get('spend_currency'):
            initial_data['spend_currency'] = self.request.session.get('spend_currency')
        return initial_data


class InvestmentContactView(GA360Mixin, FormView):  # /PS-IGNORE
    form_class = InvestmentContactForm
    template_name = 'investment/investment_contact.html'
    success_url = reverse_lazy('international_investment:investment-submission-success')

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentContactDetails',
            business_unit='Investment',
            site_section='investment-contact-details',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy('international_investment:investment-estimate')
        return context

    def form_valid(self, form):
        if not self.request.session.get('triage_data'):
            self.request.session['triage_data'] = {}
        self.request.session['triage_data'] = {**self.request.session['triage_data'], **form.cleaned_data}
        triage_data = self.request.session.get('triage_data')
        # We store the value in the session and not the
        # display which is more human readable for the agent,
        # so get/set display instead
        triage_data['location'] = get_location_display(triage_data['location'])
        self.send_email_lead_to_agent(triage_data)
        self.send_email_confirmation_to_user(triage_data)
        self.request.session['triage_data'] = {}
        return super().form_valid(form)

    def get_initial(self):
        return self.request.session.get('triage_data')

    def send_email_lead_to_agent(self, form_data):
        agent_email_address = settings.INTERNATIONAL_INVESTMENT_AGENT_EMAIL
        if agent_email_address:
            action = actions.GovNotifyEmailAction(
                template_id=settings.INTERNATIONAL_INVESTMENT_NOTIFY_AGENT_TEMPLATE_ID,
                email_address=agent_email_address,
                form_url=self.request.get_full_path(),
            )
            response = action.save(form_data)
            response.raise_for_status()

    def send_email_confirmation_to_user(self, form_data):
        action = actions.GovNotifyEmailAction(
            template_id=settings.INTERNATIONAL_INVESTMENT_NOTIFY_USER_TEMPLATE_ID,
            email_address=form_data['email_address'],
            form_url=self.request.get_full_path(),
        )
        response = action.save(form_data)
        response.raise_for_status()


class InvestmentSubmissionSuccessView(GA360Mixin, TemplateView):  # /PS-IGNORE
    template_name = 'investment/investment_success.html'

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='InvestmentSubmissionSuccess',
            business_unit='Investment',
            site_section='investment-submission-success',
        )
