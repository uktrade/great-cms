import datetime
import logging
import math
from datetime import timedelta
from uuid import uuid4

from directory_forms_api_client import actions
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import get_valid_filename
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView
from drf_spectacular.utils import extend_schema
from great_components.mixins import GA360Mixin
from icalendar import Alarm, Calendar, Event
from rest_framework.generics import GenericAPIView

from config import settings
from core import mixins as core_mixins
from core.templatetags.content_tags import format_timedelta
from directory_sso_api_client import sso_api_client
from export_academy import filters, forms, helpers, models
from export_academy.helpers import (
    calender_content,
    get_badges_for_event,
    get_buttons_for_event,
    update_booking,
)
from export_academy.mixins import (
    BookingMixin,
    HandleNewAndExistingUsersMixin,
    RegistrationMixin,
    VerificationLinksMixin,
)
from export_academy.models import ExportAcademyHomePage, Registration
from sso import helpers as sso_helpers, mixins as sso_mixins

logger = logging.getLogger(__name__)


class EventListView(GA360Mixin, core_mixins.GetSnippetContentMixin, FilterView, ListView):
    model = models.Event
    queryset = model.upcoming
    filterset_class = filters.EventFilter
    template_name = 'export_academy/event_list.html'
    paginate_by = 10

    def __init__(self):
        super().__init__()
        self.set_ga360_payload(  # from GA360Mixin
            page_id='MagnaPage',
            business_unit=settings.GA360_BUSINESS_UNIT,
            site_section='export-academy',
            site_subsection='events',
        )

    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event)

    def get_badges_for_event(self, event):
        user = self.request.user
        return get_badges_for_event(user, event)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()
        return ctx


class BookingUpdateView(BookingMixin, UpdateView):
    booking_model = models.Booking
    fields = ['status']
    notify_template = None

    def get_object(self, queryset=None):
        post_data = self.request.POST
        booking_object = self.register_booking(post_data)
        self.send_email_confirmation(booking_object, post_data)
        return booking_object

    def get_success_url(self):
        success_url = (
            'export_academy:cancellation-success' if self.object.is_cancelled else 'export_academy:booking-success'
        )
        return reverse_lazy(success_url, kwargs={'booking_id': self.object.id})


class SuccessPageView(core_mixins.GetSnippetContentMixin, TemplateView):
    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event, on_confirmation=True)

    def user_just_registered(self, booking):
        return self.request.path == reverse_lazy(
            'export_academy:registration-success', kwargs={'booking_id': booking.id}
        )

    def user_editing_registration(self):
        return self.request.path == reverse_lazy('export_academy:registration-edit-success')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()

        editing_registration = self.user_editing_registration()

        if editing_registration:
            ctx['heading'] = 'Registration update'
            ctx['editing_registration'] = editing_registration
            ctx['current_page_breadcrumb'] = 'Registration'
            return ctx

        booking = models.Booking.objects.get(id=ctx['booking_id'])
        if self.user_just_registered(booking):
            ctx['heading'] = 'Registration'
        elif booking.status == 'Confirmed':
            ctx['heading'] = 'Booking'
        else:
            ctx['heading'] = 'Cancellation'

        ctx['booking'] = booking
        ctx['event'] = booking.event

        just_registered = self.user_just_registered(booking)
        ctx['just_registered'] = just_registered
        ctx['current_page_breadcrumb'] = 'Registration' if just_registered else 'Events'
        return ctx


class EventVideoView(DetailView):
    template_name = 'export_academy/event_video.html'
    model = models.Event

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # video_render tag which helps in adding subtitles
        # needs input in specific way as below
        event: models.Event = kwargs.get('object', {})
        video = getattr(event, 'video_recording', None)
        if video:
            ctx['event_video'] = {'video': video}
            ctx['video_duration'] = format_timedelta(timedelta(seconds=event.video_recording.duration))

        document = getattr(event, 'document', None)
        completed = getattr(event, 'completed', None)

        if document and completed:
            ctx['event_document_size'] = f'{math.floor(document.file_size * 0.001)}KB' if document.file_size else '0KB'
            ctx['event_document_url'] = document.url

        return ctx

    def get(self, request, *args, **kwargs):
        update_booking(request.user.email, kwargs['pk'], request)
        return super().get(request, *args, **kwargs)


@extend_schema(exclude=True)
class DownloadCalendarView(GenericAPIView):
    event_model = models.Event

    def post(self, request, *args, **kwargs):
        post_data = self.request.POST
        event_id = post_data['event_id']
        event = self.event_model.objects.get(id=event_id)

        cal = Calendar()
        cal.add('PRODID', '-//Export academy events//')
        cal.add('VERSION', '2.0')
        meeting = Event()
        meeting.add('SUMMARY', f'UK Export Academy event - {event.name}')
        meeting.add('DTSTART', event.start_date)
        meeting.add('DTEND', event.end_date)
        meeting['LOCATION'] = event.location if event.format == event.IN_PERSON else 'Microsoft Teams Meeting'
        meeting['UID'] = uuid4()

        description = f'{event.name}\n\n{event.description}{calender_content()}'
        meeting.add('DESCRIPTION', description)

        file_name = get_valid_filename(event.name)
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')

        alert_time = timedelta(minutes=-15)
        alarm.add('trigger', alert_time)
        meeting.add_component(alarm)

        cal.add_component(meeting)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = f'inline; filename={file_name}.ics'
        return response


class RegistrationPersonalDetails(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.PersonalDetails
    model = models.Registration
    template_name = 'export_academy/registration_form_step1.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:upcoming-events'
        is_editing = False
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
            is_editing = True
        return super().get_context_data(
            **kwargs,
            is_editing=is_editing,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 1 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About you',
            email=self.request.user.email,
            current_page_breadcrumb='About you',
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-experience')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationExportExperience(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.ExportExperience
    model = models.Registration
    template_name = 'export_academy/registration_form_step2.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-details'
        is_editing = False
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
            is_editing = True
        return super().get_context_data(
            **kwargs,
            is_editing=is_editing,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 2 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About your export experience',
            current_page_breadcrumb='About your export experience',
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-business')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationBusinessDetails(core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView):
    form_class = forms.BusinessDetails
    model = models.Registration
    template_name = 'export_academy/registration_form_step3.html'

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-experience'
        is_editing = False
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
            is_editing = True
        return super().get_context_data(
            **kwargs,
            is_editing=is_editing,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 3 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='About your business',
            current_page_breadcrumb='About your business',
        )

    def get_success_url(self):
        if self.kwargs.get('edit'):
            return reverse_lazy('export_academy:registration-confirm')
        return reverse_lazy('export_academy:registration-marketing')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationMarketingSources(
    core_mixins.GetSnippetContentMixin,
    RegistrationMixin,
    FormView,
):
    form_class = forms.MarketingSources
    model = models.Registration
    template_name = 'export_academy/registration_form_step4.html'
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID

    def get_context_data(self, **kwargs):
        button_text = 'Continue'
        back_url = 'export_academy:registration-business'
        is_editing = False
        if self.kwargs.get('edit'):
            button_text = 'Save'
            back_url = 'export_academy:registration-confirm'
            is_editing = True
        return super().get_context_data(
            **kwargs,
            is_editing=is_editing,
            button_text=button_text,
            back_url=back_url,
            step_text='Step 4 of 4',
            landing_page=ExportAcademyHomePage.objects.first(),
            title='And finally...',
            current_page_breadcrumb='And finally...',
        )

    def get_success_url(self):
        return reverse_lazy('export_academy:registration-confirm')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationConfirmChoices(core_mixins.GetSnippetContentMixin, BookingMixin, RegistrationMixin, FormView):
    template_name = 'export_academy/registration_form_confirm.html'
    model = models.Registration
    booking_model = models.Booking
    form_class = forms.RegistrationConfirm
    notify_template = settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID
    booking_id = ''

    def submit_registration(self):
        reg_data = {
            'email': self.request.user.email,
            'hashed_sso_id': self.request.user.hashed_uuid,
            'first_name': self.initial_data['first_name'],
            'last_name': self.initial_data['last_name'],
            'data': self.initial_data,
        }

        if Registration.objects.filter(email=self.request.user.email).exists():
            registration = Registration.objects.get(email=self.request.user.email)
            registration.__dict__.update(**reg_data)
            registration.save()
            return

        self.model(**reg_data).save()
        self.send_gov_notify(self.initial_data)

    def confirm_booking(self, event_id):
        booking_data = dict(event_id=event_id, status=models.Booking.CONFIRMED)
        booking_object = self.register_booking(booking_data)
        del self.request.session['event_id']
        self.booking_id = booking_object.id
        self.send_email_confirmation(booking_object, booking_data)

    def form_valid(self, form):
        self.submit_registration()
        event_id = self.request.session.get('event_id')
        if event_id is not None:
            self.confirm_booking(event_id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        self.get_initial()
        is_editing = False
        if self.booking_id != '':
            is_editing = True
        return super().get_context_data(
            **kwargs,
            is_editing=is_editing,
            back_url='export_academy:registration-marketing',
            landing_page=ExportAcademyHomePage.objects.first(),
            form_data=self.initial_data,
            email=self.request.user.email,
            sectors=helpers.get_sectors_string(
                [
                    self.initial_data.get('sector', None),
                    self.initial_data.get('second_sector', None),
                    self.initial_data.get('third_sector', None),
                ]
            ),
            current_page_breadcrumb='Your answers',
        )

    def get_success_url(self):
        if self.booking_id != '':
            return reverse_lazy('export_academy:registration-success', kwargs={'booking_id': self.booking_id})
        return reverse_lazy('export_academy:registration-edit-success')


class JoinBookingView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        """
        Override redirection method to always return event link.
        """
        return self.url

    def get(self, request, *args, **kwargs):
        # Update redirect url
        event_id = kwargs.get('event_id')
        event = models.Event.objects.get(id=event_id)
        self.url = event.link

        # Update booking status to Joined
        booking = event.bookings.get(registration__email=self.request.user.email)
        booking.status = models.Booking.JOINED
        booking.save()

        return super().get(request, *args, **kwargs)


class SignUpView(HandleNewAndExistingUsersMixin, VerificationLinksMixin, sso_mixins.SignUpMixin, FormView):
    def get_template_names(self):
        if self.get_ea_user():
            return ['export_academy/accounts/create_password.html']
        else:
            return ['export_academy/accounts/signup.html']

    def get_login_url(self):
        return self.request.build_absolute_uri(reverse('export_academy:signin'))

    def handle_code_expired(self, verification_code, email):
        uidb64 = verification_code.pop('user_uidb64')
        token = verification_code.pop('verification_token')
        sso_helpers.send_verification_code_email(
            email=email,
            verification_code=verification_code,
            form_url=self.request.path,
            verification_link=self.get_verification_link(uidb64, token, user_registered=self.get_ea_user()),
            resend_verification_link=self.get_resend_verification_link(),
        )
        return HttpResponseRedirect(
            self.get_redirect_url(user_registered=self.get_ea_user(), uidb64=uidb64, token=token)
        )

    def get_redirect_url(self, uidb64=None, token=None, user_registered=False):
        redirect_url = reverse_lazy('export_academy:signup-verification')
        if uidb64 and token:
            redirect_url += f'?uidb64={uidb64}&token={token}'
            if user_registered:
                redirect_url += '&existing-ea-user=true'
        elif not (uidb64 or token) and user_registered:
            redirect_url += '?existing-ea-user=true'
        return redirect_url

    def handle_already_registered(self, email):
        sso_helpers.notify_already_registered(email=email, form_url=self.request.path, login_url=self.get_login_url())
        return HttpResponseRedirect(self.get_redirect_url(user_registered=self.get_ea_user()))

    def do_sign_up_flow(self, request):
        form = self.get_form()
        if form.is_valid():
            response = sso_api_client.user.create_user(
                email=form.cleaned_data['email'].lower(), password=form.cleaned_data['password']
            )
            if response.status_code == 400:
                self.handle_400_response(response, form)
            elif response.status_code == 409:
                email = form.cleaned_data['email'].lower()
                verification_code = sso_helpers.regenerate_verification_code(email)
                if verification_code:
                    return self.handle_code_expired(verification_code, email)
                else:
                    return self.handle_already_registered(email)
            elif response.status_code == 201:
                user_details = response.json()
                uidb64 = user_details['uidb64']
                token = user_details['verification_token']
                return self.handle_signup_success(
                    response,
                    form,
                    self.get_redirect_url(user_registered=self.get_ea_user(), uidb64=uidb64, token=token),
                    verification_link=self.get_verification_link(uidb64, token, user_registered=self.get_ea_user()),
                )

        # Ensure email address is always added to initial data
        form.initial = self.get_initial()
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.do_sign_up_flow(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] = (
            'Set password for UK Export Academy' if self.get_ea_user() else 'Join the UK Export Academy'
        )
        return context


class VerificationCodeView(VerificationLinksMixin, sso_mixins.VerifyCodeMixin, FormView):
    template_name = 'export_academy/accounts/verification_code.html'
    form_class = forms.CodeConfirmForm

    def user_ea_registered(self):
        return self.request.GET.get('existing-ea-user')

    def __init__(self):
        code_expired_error = {
            'field': 'code_confirm',
            'error_message': 'This code has expired. We have emailed you a new code',
        }
        super().__init__(code_expired_error)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_ea_user'] = self.user_ea_registered()
        context['heading'] = (
            'Set password for UK Export Academy' if self.user_ea_registered() else 'Join the UK Export Academy'
        )
        return context

    def send_welcome_notification(self, email, form_url):
        action = actions.GovNotifyEmailAction(
            template_id=settings.GOV_NOTIFY_WELCOME_TEMPLATE_ID,
            email_address=email,
            form_url=form_url,
        )
        response = action.save({})
        response.raise_for_status()
        return response

    def do_validate_code_flow(self, request):
        form = forms.CodeConfirmForm(request.POST)
        if form.is_valid():
            uidb64 = self.request.GET.get('uidb64')
            token = self.request.GET.get('token')
            code_confirm = form.cleaned_data['code_confirm']
            upstream_response = sso_api_client.user.verify_verification_code(
                {'uidb64': uidb64, 'token': token, 'code': code_confirm}
            )
            if upstream_response.status_code in [400, 404]:
                form.add_error('code_confirm', 'This code is incorrect. Please try again.')
            elif upstream_response.status_code == 422:
                # Resend verification code if it has expired.
                verification_link = self.get_verification_link(uidb64, token, user_registered=self.user_ea_registered())
                upstream_response, request, verification_link, form
                self.handle_code_expired(upstream_response, request, form, verification_link)
            else:
                redirect_url = reverse_lazy('export_academy:signup-complete')
                if self.request.GET.get('existing-ea-user'):
                    redirect_url += '?existing-ea-user=true'
                return self.handle_verification_code_success(
                    upstream_response=upstream_response, redirect_url=redirect_url
                )
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.do_validate_code_flow(request)


class SignInView(HandleNewAndExistingUsersMixin, sso_mixins.SignInMixin, FormView):
    template_name = 'export_academy/accounts/signin.html'
    success_url = reverse_lazy('export_academy:upcoming-events')

    def do_sign_in_flow(self, request):
        form = self.get_form()
        if form.is_valid():
            data = {
                'password': form.cleaned_data['password'],
                'login': form.cleaned_data['email'],
            }
            response = self.handle_post_request(
                data,
                form,
                request,
                self.success_url,
            )
            if isinstance(response, HttpResponseRedirect):
                return response

            if response:
                form.add_error('password', response)

        # Ensure email address is always added to initial data
        form.initial = self.get_initial()
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.do_sign_in_flow(request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['heading'] = 'UK Export Academy on Great.gov.uk' if self.get_ea_user() else 'Join the UK Export Academy'
        ctx['nexturl'] = self.request.META.get('HTTP_REFERER') or self.request.build_absolute_uri()
        return ctx


class EventsDetailsView(DetailView):
    template_name = 'export_academy/event_details.html'
    model = models.Event

    def get_event_types(self, event):
        return [item.name for item in event.types.all()]

    def get_warning_text(self):
        def get_video_text(self):
            if self.has_video:
                if self.signed_in:
                    return ' Event recordings are only available for 4 weeks after the event.' if self.booked else ''
                else:
                    return ' Event recordings are only available for attendees to view for 4 weeks after the event.'
            return ''

        if self.ended or self.event.completed:
            return 'This event has ended.' + get_video_text(self)

        elif self.booked:
            return ''

        elif self.event.closed:
            return 'This event is closed for bookings.' + get_video_text(self)

        return ''

    def get_context_data(self, **kwargs):
        self.event: models.Event = kwargs.get('object', {})
        self.video = getattr(self.event, 'video_recording', None)
        self.user = self.request.user
        current_datetime = datetime.datetime.now(datetime.timezone.utc)
        self.ended = self.event.end_date < current_datetime
        self.has_video = True if self.video else False
        self.signed_in = True if self.request.user != AnonymousUser() else False
        self.booked = helpers.user_booked_on_event(self.user, self.event)
        self.warning_call_to_action = self.get_warning_call_to_action()

        ctx = super().get_context_data(**kwargs)
        ctx['ended'] = self.ended
        ctx['has_video'] = self.has_video
        ctx['event_types'] = self.get_event_types(self.event)
        ctx['speakers'] = [speaker_object.speaker for speaker_object in self.event.event_speakers.all()]
        ctx['signed_in'] = self.signed_in
        ctx['booked'] = self.booked
        ctx['warning_text'] = self.get_warning_text()
        ctx['warning_call_to_action'] = self.warning_call_to_action
        return ctx

    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event)

    def get_badges_for_event(self, event):
        user = self.request.user
        return get_badges_for_event(user, event)

    def get_warning_call_to_action(self):
        if self.ended or self.event.completed or self.event.closed:
            view_more_events = '<a class="govuk-link" href="../">View more events</a>'
            if self.has_video:
                if self.signed_in:
                    if self.booked:
                        return f"""<a class='govuk-link' href='../event/{ self.event.id }'>
                    Watch now<span class="govuk-visually-hidden">{self.event.id}</span></a>"""
                    else:
                        return view_more_events
                registration_link = redirect(
                    reverse_lazy('export_academy:registration', kwargs=dict(event_id=self.event.id))
                )
                return f"""<a class='govuk-link'∂ href='../../../{ registration_link.url }'>
            Sign in to watch<span class="govuk-visually-hidden">{self.event.id}</span></a>"""

            else:
                return view_more_events
        return ''

    def get_object(self, **kwargs):
        return self.model.objects.get(slug=self.kwargs['slug'])


class SignUpCompleteView(TemplateView):
    template_name = 'export_academy/accounts/signup_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_ea_user'] = self.request.GET.get('existing-ea-user')
        return context
