import pickle

from directory_forms_api_client import actions
from directory_forms_api_client.forms import GovNotifyEmailActionMixin
from django.urls import reverse

from config import settings
from export_academy import helpers
from export_academy.models import Registration
from sso_profile.enrolment.constants import RESEND_VERIFICATION


class BookingMixin(GovNotifyEmailActionMixin):
    def register_booking(self, data):
        registration = Registration.objects.get(email=self.request.user.email)
        booking_data = dict(event_id=data['event_id'], registration=registration, defaults={'status': data['status']})
        booking_object, _created = self.get_or_save_object(booking_data)
        return booking_object

    def send_email_confirmation(self, booking_object, post_data):
        if post_data['status'] == booking_object.CONFIRMED:
            if settings.FEATURE_USE_BGS_TEMPLATES:
                pass
            else:
                template_id = settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID
            self.notify_template = template_id
        else:
            if settings.FEATURE_USE_BGS_TEMPLATES:
                pass
            else:
                template_id = settings.EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID
            self.notify_template = template_id

        notify_data = dict(
            first_name=booking_object.registration.first_name,
            event_names=booking_object.event.name,
            event_url=booking_object.event.get_absolute_url(),
        )
        self.send_gov_notify(notify_data)

    def save_model(self, data):
        self.model(**data).save()

    def get_or_save_object(self, data):
        return self.booking_model.objects.get_or_create(**data)

    def send_gov_notify(self, data):
        action = actions.GovNotifyEmailAction(
            email_address=self.request.user.email,
            template_id=self.notify_template,
            form_url=self.request.get_full_path(),
        )
        response = action.save(data)
        response.raise_for_status()


class RegistrationMixin:
    initial_data = {}

    def get_initial(self):
        initial = super().get_initial()
        if self.kwargs.get('event_id'):
            self.request.session['event_id'] = str(self.kwargs.get('event_id'))
        data = self.request.session.get('form_data')
        if data is not None:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        if Registration.objects.filter(email=self.request.user.email).exists():
            self.initial_data = initial = {
                **getattr(Registration.objects.get(email=self.request.user.email), 'data'),
                **self.initial_data,
            }
        return initial

    def save_registration(self, form):
        cleaned_data = form.cleaned_data

        reg_data = ({**self.initial_data, **cleaned_data},)

        reg_data = pickle.dumps(reg_data).hex()
        self.request.session['form_data'] = reg_data


class VerificationLinksMixin:
    def get_verification_link(self, uidb64, token, user_registered, next_param=None):
        verification_params = f'?uidb64={uidb64}&token={token}'
        url = self.request.build_absolute_uri(reverse('export_academy:signup-verification')) + verification_params

        if next_param is None:
            next_param = self.request.GET.get('next', '')
        if next_param:
            url += f'&next={next_param}'
        if user_registered:
            url += '&existing-ea-user=true'
        return url

    def get_resend_verification_link(self):
        return self.request.build_absolute_uri(
            reverse('sso_profile:resend-verification', kwargs={'step': RESEND_VERIFICATION})
        )


class HandleNewAndExistingUsersMixin:
    def get_ea_user(self):
        idb64 = self.request.GET.get('idb64')
        token = self.request.GET.get('token')
        if token and idb64:
            return helpers.get_registration_from_unique_link(idb64, token)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_ea_user'] = self.get_ea_user() is not None
        return context

    def get_initial(self):
        initial = super().get_initial()
        if self.get_ea_user():
            initial['email'] = self.get_ea_user().email
        return initial
