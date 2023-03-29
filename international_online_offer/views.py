from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from international_online_offer import forms
from international_online_offer.models import TriageData

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

    def get_initial(self):
        inital_sector = self.request.session.get('sector')
        if self.request.user.is_authenticated:
            try:
                triage_data = TriageData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            except TriageData.DoesNotExist:
                triage_data = None
            if triage_data and triage_data.sector:
                inital_sector = triage_data.sector

        return {'sector': inital_sector}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid, defaults={"sector": form.cleaned_data['sector']}
            )
        else:
            self.request.session['sector'] = form.cleaned_data['sector']
        return super().form_valid(form)


class IOOIntent(FormView):
    form_class = forms.IntentForm
    template_name = 'ioo/triage/intent.html'
    success_url = reverse_lazy('international_online_offer:location')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:sector',
            step_text='Step 2 of 5',
            question_text='How do you plan to expand your business in the UK?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your expansion plans.""",
        )

    def get_initial(self):
        inital_intent = self.request.session.get('intent')
        inital_intent_other = self.request.session.get('intent_other')
        if self.request.user.is_authenticated:
            try:
                triage_data = TriageData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            except TriageData.DoesNotExist:
                triage_data = None
            if triage_data and triage_data.intent:
                inital_intent = triage_data.intent
            if triage_data and triage_data.intent_other:
                inital_intent_other = triage_data.intent_other

        return {'intent': inital_intent, 'intent_other': inital_intent_other}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={"intent": form.cleaned_data['intent'], "intent_other": form.cleaned_data['intent_other']},
            )
        else:
            self.request.session['intent'] = form.cleaned_data['intent']
            self.request.session['intent_other'] = form.cleaned_data['intent_other']
        return super().form_valid(form)


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

    def get_initial(self):
        inital_location = self.request.session.get('location')
        inital_location_none = self.request.session.get('location_none')
        if self.request.user.is_authenticated:
            try:
                triage_data = TriageData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            except TriageData.DoesNotExist:
                triage_data = None
            if triage_data:
                if triage_data.location:
                    inital_location = triage_data.location
                if triage_data.location_none:
                    inital_location_none = triage_data.location_none

        return {'location': inital_location, 'location_none': inital_location_none}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    "location": form.cleaned_data['location'],
                    "location_none": form.cleaned_data['location_none'],
                },
            )
        else:
            self.request.session['location'] = form.cleaned_data['location']
            self.request.session['location_none'] = form.cleaned_data['location_none']
        return super().form_valid(form)


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

    def get_initial(self):
        inital_hiring = self.request.session.get('hiring')
        if self.request.user.is_authenticated:
            try:
                triage_data = TriageData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            except TriageData.DoesNotExist:
                triage_data = None
            if triage_data and triage_data.hiring:
                inital_hiring = triage_data.hiring

        return {'hiring': inital_hiring}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid, defaults={"hiring": form.cleaned_data['hiring']}
            )
        else:
            self.request.session['hiring'] = form.cleaned_data['hiring']
        return super().form_valid(form)


class IOOSpend(FormView):
    form_class = forms.SpendForm
    template_name = 'ioo/triage/spend.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            back_url='international_online_offer:hiring',
            step_text='Step 5 of 5',
            question_text='What is your planned spend for UK entry or expansion?',
            why_we_ask_this_question_text="""We'll use this information to provide customised content
              relevant to your spend.""",
        )

    def get_initial(self):
        inital_spend = self.request.session.get('spend')
        inital_spend_other = self.request.session.get('spend_other')
        if self.request.user.is_authenticated:
            try:
                triage_data = TriageData.objects.get(hashed_uuid=self.request.user.hashed_uuid)
            except TriageData.DoesNotExist:
                triage_data = None
            if triage_data:
                if triage_data.spend:
                    inital_spend = triage_data.spend
                if triage_data.spend_other:
                    inital_spend_other = triage_data.spend_other

        return {'spend': inital_spend, 'spend_other': inital_spend_other}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={"spend": form.cleaned_data['spend'], "spend_other": form.cleaned_data['spend_other']},
            )
        else:
            self.request.session['spend'] = form.cleaned_data['spend']
            self.request.session['spend_other'] = form.cleaned_data['spend_other']
        return super().form_valid(form)


class IOOContact(FormView):
    form_class = forms.ContactForm
    template_name = 'ioo/contact.html'
    success_url = '/international/expand-your-business-in-the-uk/guide/?success=true'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            complete_contact_form_message=LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE,
            back_url='/international/expand-your-business-in-the-uk/guide/',
        )


class IOOLogin(FormView):
    form_class = forms.LoginForm
    template_name = 'ioo/login.html'
    success_url = reverse_lazy('international_online_offer:signup')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )


class IOOSignUp(FormView):
    form_class = forms.SignUpForm
    template_name = 'ioo/signup.html'
    success_url = reverse_lazy('international_online_offer:login')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )


class IOOLogin(FormView):
    form_class = forms.LoginForm
    template_name = 'ioo/login.html'
    success_url = reverse_lazy('international_online_offer:signup')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )


class IOOSignUp(FormView):
    form_class = forms.SignUpForm
    template_name = 'ioo/signup.html'
    success_url = reverse_lazy('international_online_offer:login')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
        )
