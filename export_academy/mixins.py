import pickle

from directory_forms_api_client import actions
from directory_forms_api_client.forms import GovNotifyEmailActionMixin

from config import settings
from export_academy.models import Registration


class BookingMixin(GovNotifyEmailActionMixin):
    def register_booking(self, data):
        booking_data = dict(
            event_id=data['event_id'], registration_id=self.request.user.email, defaults={'status': data['status']}
        )
        booking_object, _created = self.get_or_save_object(booking_data)
        return booking_object

    def send_email_confirmation(self, booking_object, post_data):
        if post_data['status'] == booking_object.CONFIRMED:
            self.notify_template = settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID
        else:
            self.notify_template = settings.EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID

        notify_data = dict(first_name=booking_object.registration.first_name, event_names=booking_object.event.name)
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
        if self.kwargs.get('booking_id'):
            self.request.session['booking_id'] = str(self.kwargs.get('booking_id'))
        data = self.request.session.get('form_data')
        if data is not None:
            self.initial_data = initial = pickle.loads(bytes.fromhex(data))[0]
        if Registration.objects.filter(email=self.request.user.email).exists():
            self.initial_data = {
                **getattr(Registration.objects.get(email=self.request.user.email), 'data'),
                **self.initial_data,
            }
        return initial

    def save_registration(self, form):
        cleaned_data = form.cleaned_data

        reg_data = ({**self.initial_data, **cleaned_data},)

        reg_data = pickle.dumps(reg_data).hex()
        self.request.session['form_data'] = reg_data
