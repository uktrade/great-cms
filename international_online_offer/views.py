from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from international_online_offer import forms
from international_online_offer.core import scorecard
from international_online_offer.models import (
    TriageData,
    UserData,
    get_triage_data,
    get_triage_data_from_db_or_session,
    get_user_data,
)

LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = 'Complete the contact form to keep up to date with our personalised service.'
HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = """Your business qualifies for 1 to 1 support from specialist UK government
 advisors. Complete the form to access this and keep up to date with our personalised service."""
COMPLETED_CONTACT_FORM_MESSAGE = 'Thank you for completing the contact form.'


def calculate_and_store_is_high_value(request):
    existing_triage_data = get_triage_data_from_db_or_session(request)
    is_high_value = scorecard.score_is_high_value(
        existing_triage_data.sector,
        existing_triage_data.location,
        existing_triage_data.hiring,
        existing_triage_data.spend,
        existing_triage_data.spend_other,
    )
    if request.user.is_authenticated:
        TriageData.objects.update_or_create(
            hashed_uuid=request.user.hashed_uuid, defaults={'is_high_value': is_high_value}
        )
    else:
        request.session['is_high_value'] = is_high_value


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
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'sector': triage_data.sector}

        return {'sector': self.request.session.get('sector')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'sector': form.cleaned_data['sector'],
                },
            )
        else:
            self.request.session['sector'] = form.cleaned_data['sector']
        calculate_and_store_is_high_value(self.request)
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
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'intent': triage_data.intent, 'intent_other': triage_data.intent_other}

        return {'intent': self.request.session.get('intent'), 'intent_other': self.request.session.get('intent_other')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'intent': form.cleaned_data['intent'],
                    'intent_other': form.cleaned_data['intent_other'],
                },
            )
        else:
            self.request.session['intent'] = form.cleaned_data['intent']
            self.request.session['intent_other'] = form.cleaned_data['intent_other']
        calculate_and_store_is_high_value(self.request)
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
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'location': triage_data.location, 'location_none': triage_data.location_none}

        return {
            'location': self.request.session.get('location'),
            'location_none': self.request.session.get('location_none'),
        }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'location': form.cleaned_data['location'],
                    'location_none': form.cleaned_data['location_none'],
                },
            )
        else:
            self.request.session['location'] = form.cleaned_data['location']
            self.request.session['location_none'] = form.cleaned_data['location_none']
        calculate_and_store_is_high_value(self.request)
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
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'hiring': triage_data.hiring}

        return {'hiring': self.request.session.get('hiring')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'hiring': form.cleaned_data['hiring'],
                },
            )
        else:
            self.request.session['hiring'] = form.cleaned_data['hiring']
        calculate_and_store_is_high_value(self.request)
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
        if self.request.user.is_authenticated:
            triage_data = get_triage_data(self.request.user.hashed_uuid)
            if triage_data:
                return {'spend': triage_data.spend, 'spend_other': triage_data.spend_other}

        return {'spend': self.request.session.get('spend'), 'spend_other': self.request.session.get('spend_other')}

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            TriageData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults={
                    'spend': form.cleaned_data['spend'],
                    'spend_other': form.cleaned_data['spend_other'],
                },
            )
        else:
            self.request.session['spend'] = form.cleaned_data['spend']
            self.request.session['spend_other'] = form.cleaned_data['spend_other']
        calculate_and_store_is_high_value(self.request)
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

    def get_initial(self):
        if self.request.user.is_authenticated:
            user_data = get_user_data(self.request.user.hashed_uuid)
            if user_data:
                return {
                    'company_name': user_data.company_name,
                    'company_location': user_data.company_location,
                    'full_name': user_data.full_name,
                    'role': user_data.role,
                    'email': user_data.email,
                    'telephone_number': user_data.telephone_number,
                    'agree_terms': user_data.agree_terms,
                    'agree_info_email': user_data.agree_info_email,
                    'agree_info_telephone': user_data.agree_info_telephone,
                }

        return {
            'company_name': self.request.session.get('company_name'),
            'company_location': self.request.session.get('company_location'),
            'full_name': self.request.session.get('full_name'),
            'role': self.request.session.get('role'),
            'email': self.request.session.get('email'),
            'telephone_number': self.request.session.get('telephone_number'),
            'agree_terms': self.request.session.get('agree_terms'),
            'agree_info_email': self.request.session.get('agree_info_email'),
            'agree_info_telephone': self.request.session.get('agree_info_telephone'),
        }

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            UserData.objects.update_or_create(
                hashed_uuid=self.request.user.hashed_uuid,
                defaults=form.cleaned_data,
            )
        else:
            self.request.session['company_name'] = form.cleaned_data['company_name']
            self.request.session['company_location'] = form.cleaned_data['company_location']
            self.request.session['full_name'] = form.cleaned_data['full_name']
            self.request.session['role'] = form.cleaned_data['role']
            self.request.session['email'] = form.cleaned_data['email']
            self.request.session['telephone_number'] = form.cleaned_data['telephone_number']
            self.request.session['agree_terms'] = form.cleaned_data['agree_terms']
            self.request.session['agree_info_email'] = form.cleaned_data['agree_info_email']
            self.request.session['agree_info_telephone'] = form.cleaned_data['agree_info_telephone']
        return super().form_valid(form)


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
