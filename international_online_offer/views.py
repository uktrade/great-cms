from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from international_online_offer import forms


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
    success_url = reverse_lazy('international_online_offer:index')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:intent',
            step_text='Step 3 of 5',
            question_text='Where in the UK would you like to expand your business?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your city, county or region.""",
        )
