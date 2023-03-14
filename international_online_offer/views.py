import random

from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from international_online_offer import forms

LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = 'Complete the contact form to keep up to date with our personalised service.'
HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = """Your business qualifies for 1 to 1 support from specialist UK government
 advisors. Complete the form to access this and keep up to date with our personalised service."""
COMPLETED_CONTACT_FORM_MESSAGE = 'Thank you for completing the contact form.'


class IOOIndex(TemplateView):
    template_name = 'ioo/index.html'


class IOOSector(FormView):
    form_class = forms.SectorForm
    template_name = 'ioo/triage/sector.html'
    success_url = reverse_lazy('international_online_offer:intent')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:index',
            step_text='Step 1 of 5',
            question_text='What is your business sector?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your sector and products or services.""",
        )


class IOOIntent(FormView):
    form_class = forms.IntentForm
    template_name = 'ioo/triage/intent.html'
    success_url = reverse_lazy('international_online_offer:location')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:sector',
            step_text='Step 2 of 5',
            question_text='How do you plan to expand your business into the UK?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your expansion plans.""",
        )


class IOOLocation(FormView):
    form_class = forms.LocationForm
    template_name = 'ioo/triage/location.html'
    success_url = reverse_lazy('international_online_offer:hiring')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:intent',
            step_text='Step 3 of 5',
            question_text='Where in the UK would you like to expand your business?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your city, county or region.""",
        )


class IOOHiring(FormView):
    form_class = forms.HiringForm
    template_name = 'ioo/triage/hiring.html'
    success_url = reverse_lazy('international_online_offer:spend')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:location',
            step_text='Step 4 of 5',
            question_text='How many people are you looking to hire in the UK?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your hiring.""",
        )


class IOOSpend(FormView):
    form_class = forms.SpendForm
    template_name = 'ioo/triage/spend.html'
    success_url = '/international/international-online-offer/guide/'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:hiring',
            step_text='Step 5 of 5',
            question_text='What is your planned spend for UK entry or expansion?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your spend.""",
        )


class IOOContact(FormView):
    form_class = forms.ContactForm
    template_name = 'ioo/contact.html'
    success_url = '/international/international-online-offer/guide/?success=true'
    high_value_investor = False

    def get_context_data(self, **kwargs):
        self.high_value_investor = random.choice([True, False])
        if not self.high_value_investor:
            complete_contact_form_message = LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
        else:
            complete_contact_form_message = HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE

        return super().get_context_data(
            **kwargs,
            high_value_investor=self.high_value_investor,
            complete_contact_form_message=complete_contact_form_message,
            back_url='/international/international-online-offer/guide/',
        )
