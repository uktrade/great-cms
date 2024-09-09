import json
import logging
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from directory_forms_api_client import actions
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
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
from great_components.helpers import get_is_authenticated, get_user
from great_components.mixins import GA360Mixin
from icalendar import Alarm, Calendar, Event
from rest_framework.generics import GenericAPIView

from config import settings
from core import mixins as core_mixins
from core.forms import HCSATForm
from core.helpers import get_location
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
from export_academy.models import (
    Booking,
    ExportAcademyHomePage,
    Registration,
    VideoOnDemandPageTracking,
)
from sso import helpers as sso_helpers, mixins as sso_mixins
from sso.models import BusinessSSOUser

logger = logging.getLogger(__name__)


class GetBreadcrumbsMixin:

    @property
    def get_breadcrumbs(self):
        return [
            {'title': 'UK Export Academy', 'url': '/export-academy/'},
        ]


class BespokeBreadcrumbMixin(TemplateView):

    def get_context_data(self, **kwargs):
        bespoke_breadcrumbs = [
            {'title': 'UK Export Academy', 'url': '/export-academy/'},
            {'title': 'Events', 'url': reverse('export_academy:upcoming-events')},
        ]
        return super().get_context_data(bespoke_breadcrumbs=bespoke_breadcrumbs, **kwargs)


class EventListView(GetBreadcrumbsMixin, GA360Mixin, core_mixins.GetSnippetContentMixin, FilterView, ListView):
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
        market_filters = sector_filters = region_filters = trading_bloc_filters = False
        ctx = super().get_context_data(**kwargs)
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()
        if self.filterset_class.declared_filters['market'].queryset.count() > 0 and settings.FEATURE_UKEA_MARKET_FILTER:
            market_filters = True
        if self.filterset_class.declared_filters['sector'].queryset.count() > 0 and settings.FEATURE_UKEA_SECTOR_FILTER:
            sector_filters = True
        if self.filterset_class.declared_filters['region'].queryset.count() > 0 and settings.FEATURE_UKEA_REGION_FILTER:
            region_filters = True
        if (
            self.filterset_class.declared_filters['trading_bloc'].queryset.count() > 0
            and settings.FEATURE_UKEA_TRADING_BLOC_FILTER
        ):
            trading_bloc_filters = True
        ctx['market_filters'] = market_filters
        ctx['sector_filters'] = sector_filters
        ctx['region_filters'] = region_filters
        ctx['trading_bloc_filters'] = trading_bloc_filters
        ctx['bespoke_breadcrumbs'] = self.get_breadcrumbs
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


class SuccessPageView(GetBreadcrumbsMixin, core_mixins.GetSnippetContentMixin, core_mixins.HCSATMixin, FormView):

    form_class = HCSATForm
    hcsat_service_name = 'export_academy'

    def get_success_url(self):
        return reverse_lazy('export_academy:registration-success', kwargs={'booking_id': self.kwargs.get('booking_id')})

    def get_buttons_for_event(self, event):
        user = self.request.user
        return get_buttons_for_event(user, event, on_confirmation=True)

    def user_just_registered(self, booking):
        return self.request.path == reverse_lazy(
            'export_academy:registration-success', kwargs={'booking_id': booking.id}
        )

    def user_editing_registration(self):
        return self.request.path == reverse_lazy('export_academy:registration-edit-success')

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        """
        id = self.kwargs.get('booking_id')
        obj = models.Booking.objects.get(id=id)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['bespoke_breadcrumbs'] = self.get_breadcrumbs
        ctx['landing_page'] = models.ExportAcademyHomePage.objects.first()
        editing_registration = self.user_editing_registration()

        if editing_registration:
            ctx['heading'] = 'Registration update'
            ctx['editing_registration'] = editing_registration
            ctx['current_page_breadcrumb'] = 'Registration'
            return ctx
        booking = self.get_object()
        if self.user_just_registered(booking):
            ctx['heading'] = 'Registration'
            ctx['return_url'] = booking.event.get_absolute_url()
            ctx['return_msg'] = 'Back to event'
        elif booking.status == 'Confirmed':
            ctx['heading'] = 'Booking'
            ctx['return_url'] = booking.event.get_absolute_url()
            ctx['return_msg'] = 'Back to event'
        else:
            ctx['heading'] = 'Cancellation'
            ctx['return_url'] = reverse('export_academy:upcoming-events')
            ctx['return_msg'] = 'Explore more events'

        ctx['booking'] = booking
        ctx['event'] = booking.event

        just_registered = self.user_just_registered(booking)
        ctx['just_registered'] = just_registered
        ctx['current_page_breadcrumb'] = 'Registration' if just_registered else 'Events'

        hcsat = self.get_hcsat(self.hcsat_service_name)
        form = self.form_class(instance=hcsat)
        ctx['hcsat_form'] = form
        ctx['hcsat'] = hcsat

        return ctx

    def post(self, request, *args, **kwargs):
        form_class = self.form_class

        hcsat = self.get_hcsat(self.hcsat_service_name)
        post_data = self.request.POST

        if 'cancelButton' in post_data:
            """
            Redirect user if 'cancelButton' is found in the POST data
            """
            if hcsat:
                hcsat.stage = 2
                hcsat.save()
            return HttpResponseRedirect(self.get_success_url())

        form = form_class(post_data)

        if form.is_valid():
            if hcsat:
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

        hcsat = form.save(commit=False)
        booking = self.get_object()

        # Apply data specific to this service
        hcsat.URL = reverse_lazy('export_academy:registration-success', kwargs={'booking_id': booking.id})
        hcsat.user_journey = 'EVENT_BOOKING'
        hcsat.session_key = self.request.session.session_key
        hcsat.save()

        self.request.session[f'{self.hcsat_service_name}_hcsat_id'] = hcsat.id

        if 'js_enabled' in self.request.get_full_path():
            return JsonResponse({'pk': hcsat.pk})
        return HttpResponseRedirect(self.get_success_url())


class EventVideoView(DetailView):
    template_name = 'export_academy/event_video.html'
    model = models.Event

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # video_render tag which helps in adding subtitles
        # needs input in specific way as below
        event: self.model = kwargs.get('object', {})
        video = getattr(event, 'video_recording', None)
        if video:
            ctx['event_video'] = {'video': video}
            ctx['video_duration'] = format_timedelta(timedelta(seconds=event.video_recording.duration))

        bespoke_breadcrumbs = [
            {'title': 'Back to event', 'url': event.get_absolute_url()},
        ]
        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs

        if not event.name or not video:
            raise Http404

        document = getattr(event, 'document', None)
        completed = getattr(event, 'completed', None)

        if document and completed:
            ctx['event_document_size'] = f'{math.floor(document.file_size * 0.001)}KB' if document.file_size else '0KB'
            ctx['event_document_url'] = document.url
        return ctx

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        if request.user.is_authenticated:
            update_booking(request.user.email, pk, request)
        else:
            event = get_object_or_404(self.model, pk=pk)
            return HttpResponseRedirect(event.get_absolute_url())
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

        description = f'{event.name}\n\n{event.description}{calender_content(event.get_absolute_url())}'
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


class RegistrationPersonalDetails(
    BespokeBreadcrumbMixin, core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView
):
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


class RegistrationExportExperience(
    BespokeBreadcrumbMixin, core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView
):
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


class RegistrationBusinessDetails(
    BespokeBreadcrumbMixin, core_mixins.GetSnippetContentMixin, RegistrationMixin, FormView
):
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
    BespokeBreadcrumbMixin,
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
            title='How did you hear about the UK Export Academy?',
            hide_title=True,  # Hide title in base template so that heading is within radio legend
            current_page_breadcrumb='How did you hear about the UK Export Academy?',
        )

    def get_success_url(self):
        return reverse_lazy('export_academy:registration-confirm')

    def form_valid(self, form):
        self.save_registration(form)
        return super().form_valid(form)


class RegistrationConfirmChoices(
    BespokeBreadcrumbMixin, core_mixins.GetSnippetContentMixin, BookingMixin, RegistrationMixin, FormView
):
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
        next = self.request.GET.get('next', '')
        redirect_url = reverse_lazy('export_academy:signup-verification')
        if uidb64 and token:
            redirect_url += f'?uidb64={uidb64}&token={token}'
            if user_registered:
                redirect_url += '&existing-ea-user=true'
            if next:
                redirect_url += f'&next={next}'
        elif not (uidb64 or token) and user_registered:
            redirect_url += '?existing-ea-user=true'
        elif next:
            redirect_url += f'?next={next}'
        return redirect_url

    def handle_already_registered(self, email):
        sso_helpers.notify_already_registered(email=email, form_url=self.request.path, login_url=self.get_login_url())
        return HttpResponseRedirect(self.get_redirect_url(user_registered=self.get_ea_user()))

    def get_form_class(self):
        if self.get_ea_user():
            return forms.ChoosePasswordForm
        else:
            return forms.SignUpForm

    def do_sign_up_flow(self, request):
        form = self.get_form()
        if form.is_valid():
            response = sso_api_client.user.create_user(
                email=form.cleaned_data['email'].lower(),
                password=form.cleaned_data['password'],
                mobile_phone_number=form.cleaned_data['mobile_phone_number'],
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
        context['next'] = self.request.GET.get('next')
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
        context['next'] = self.request.GET.get('next')
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
            next = self.request.GET.get('next')
            existing_ea_user = self.request.GET.get('existing-ea-user')
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
                if existing_ea_user:
                    redirect_url += '?existing-ea-user=true'
                    if next:
                        redirect_url += f'&next={next}'
                elif next:
                    redirect_url += f'?next={next}'
                return self.handle_verification_code_success(
                    upstream_response=upstream_response, redirect_url=redirect_url
                )
        return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.do_validate_code_flow(request)


class SignInView(HandleNewAndExistingUsersMixin, sso_mixins.SignInMixin, FormView):
    template_name = 'export_academy/accounts/signin.html'
    success_url = reverse_lazy('export_academy:upcoming-events')

    def get_success_url(self):
        next = self.request.GET.get('next')
        return self.success_url if not next else next

    def get_form_class(self):
        if self.get_ea_user():
            return forms.ChoosePasswordForm
        else:
            return forms.SignInForm

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
                self.get_success_url(),
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
        ctx['next'] = self.request.GET.get('next')
        ctx['heading'] = 'UK Export Academy on Great.gov.uk' if self.get_ea_user() else 'Join the UK Export Academy'
        return ctx


class EventsDetailsView(DetailView):
    template_name = 'export_academy/event_details.html'
    model = models.Event

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
        self.ended = self.event.has_ended()
        self.has_video = True if self.video else False
        self.signed_in = True if self.request.user != AnonymousUser() else False
        self.booked = helpers.user_booked_on_event(self.user, self.event)
        self.warning_call_to_action = self.get_warning_call_to_action()

        ctx = super().get_context_data(**kwargs)
        ctx['ended'] = self.ended
        ctx['has_video'] = self.has_video
        ctx['event_types'] = self.event.get_event_types()
        ctx['speakers'] = self.event.get_speakers()
        ctx['signed_in'] = self.signed_in
        ctx['booked'] = self.booked
        ctx['warning_text'] = self.get_warning_text()
        ctx['warning_call_to_action'] = self.warning_call_to_action
        ctx['has_event_badges'] = len(self.get_badges_for_event(self.event)) > 0
        ctx['series'] = self.event.get_course()[0] if len(self.event.get_course()) else None
        ctx['show_past_events'] = True
        ctx['bespoke_breadcrumbs'] = [
            {'title': 'UK Export Academy', 'url': ''},  # what is the url?
            {'title': 'Events', 'url': ''},  # what is the url?
        ]
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
                        return f"""<a class='govuk-link' href='../../event/{ self.event.id }'>
                    Watch <span class="govuk-visually-hidden">event recording</span>now</a>"""
                    else:
                        return view_more_events
                registration_link = redirect(
                    reverse_lazy('export_academy:registration', kwargs=dict(event_id=self.event.id))
                )
                return f"""<a class='govuk-link'∂ href='../../..{ registration_link.url }'>
            Sign in to watch<span class="govuk-visually-hidden"> event recording</span></a>"""

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
        context['next'] = self.request.GET.get('next')
        return context


class EACourseView(TemplateView):
    template_name = 'export_academy/course_page.html'

    def get_context_data(self, **kwargs):
        self.page = get_list_or_404(models.CoursePage, live=True, slug=kwargs['slug'])[0]
        ctx = super().get_context_data(**kwargs)
        ctx['signed_in'] = True if self.request.user != AnonymousUser() else False
        ctx['page'] = self.page
        ctx['bespoke_breadcrumbs'] = [{'title': 'UK Export Academy', 'url': ''}]  # what is the url?
        return ctx


@method_decorator(transaction.non_atomic_requests, name='dispatch')
class EventVideoOnDemandView(GetBreadcrumbsMixin, DetailView):
    template_name = 'export_academy/event_on_demand_video.html'
    model = models.Event

    slug = None
    event_slug = None
    recording_date = None
    recorded_datetime = None
    event = None
    video = None

    NO_COMPANY_INFO = ('', '', '')

    def extract_date_and_event_name(self, input_string):
        # Define a regular expression pattern for extracting the date
        date_pattern = r'(\d{2}-[a-zA-Z]+-\d{4})$'

        # Use re.search to find the match at the end of the string
        date_match = re.search(date_pattern, input_string)

        if date_match:
            # Extract the date from the match
            date = date_match.group(1)

            # Get the remaining part of the string before the date
            text_before_date = input_string[: date_match.start()].rstrip('-').strip()

            return text_before_date, date
        else:
            # If no date is found, return None for both parts
            return None, None

    def _user_has_accepted_cookies(self):
        cookies = json.loads(self.request.COOKIES.get('cookies_policy', '{}'))  # noqa: P103
        return cookies.get('usage', False)

    def _get_location(self):
        return get_location(self.request)

    def _get_region(self):
        location = self._get_location()
        if not location:
            return None
        return location.get('region', None)

    def _get_company_details(self, user):
        if not isinstance(user, BusinessSSOUser):
            return self.NO_COMPANY_INFO

        company = user.company
        if not company:
            return self.NO_COMPANY_INFO
        # 16/11/2023 company telephone number requested by Users but we do not capture this at the moment
        return (company.name, company.postcode, '')

    def _get_registration_and_booking(self, user_email):
        registration = Registration.objects.filter(email=user_email).first()
        if not registration:
            return None, None
        booking = Booking.objects.filter(event=self.event, registration=registration).first()
        if not booking:
            return registration, None
        return registration, booking

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.event:
            self._get_event_details()
        user = get_user(self.request)
        is_logged_in = get_is_authenticated(self.request)
        if user and is_logged_in and self.event and self.video and user.email:
            already_tracked = VideoOnDemandPageTracking.user_already_recorded(user.email, self.event, self.video)
            if not already_tracked:
                cookies_accepted_on_details_view = self._user_has_accepted_cookies()
                details_viewed = datetime.now(timezone.utc)
                company_name, company_postcode, company_phone = self._get_company_details(user)
                registration, booking = self._get_registration_and_booking(user)

                VideoOnDemandPageTracking.objects.create(
                    id=uuid4(),
                    user_email=user.email,
                    hashed_uuid=user.hashed_uuid if isinstance(user, BusinessSSOUser) else None,
                    region=self._get_region(),
                    company_name=company_name,
                    company_postcode=company_postcode,
                    company_phone=company_phone,
                    details_viewed=details_viewed,
                    cookies_accepted_on_details_view=cookies_accepted_on_details_view,
                    event=self.event,
                    booking=booking,
                    registration=registration,
                    hashed_sso_id=registration.hashed_sso_id if registration else None,
                    video=self.video,
                )

        return super().get(request, *args, **kwargs)

    def _get_event_details(self):
        self.slug = self.kwargs.pop('slug', None)
        if not self.slug:
            raise Http404
        self.event_slug, self.recording_date = self.extract_date_and_event_name(self.slug)
        self.recorded_datetime = datetime.strptime(self.recording_date, '%d-%B-%Y').date()
        self.event, self.video = self._get_event_and_video()
        if not self.event or not self.video:
            raise Http404

    def get_object(self, queryset=None):
        if not self.event:
            self._get_event_details()
        self.kwargs['pk'] = self.event.id
        obj = super().get_object(queryset=None)
        if obj:
            return obj
        raise Http404

    def _get_event_and_video(self):
        # event is set to the next live occurence of the current event
        event = models.Event.objects.filter(
            slug__contains=self.event_slug,
            past_event_recorded_date__date=self.recorded_datetime,
            start_date__gte=datetime.now(),
        ).last()
        video = getattr(event, 'past_event_video_recording', None)
        return event, video

    def get_context_data(self, **kwargs):
        self.user = self.request.user
        self.signed_in = True if self.request.user != AnonymousUser() else False
        ctx = super().get_context_data(**kwargs)

        # video_render tag which helps in adding subtitles
        # needs input in specific way as below
        event: models.Event = kwargs.get('object', {})
        video = getattr(event, 'past_event_video_recording', None)
        if video:
            ctx['event_video'] = {'video': video}
            ctx['video_duration'] = format_timedelta(timedelta(seconds=event.past_event_video_recording.duration))
            thumbnail = getattr(ctx['event_video']['video'], 'thumbnail', None)
            if thumbnail._file:
                ctx['video_thumbnail'] = thumbnail

        document = getattr(event, 'past_event_presentation_file', None)
        ctx['event_document_url'] = document.url if document else None
        ctx['speakers'] = event.get_speakers()
        ctx['event_types'] = event.get_event_types()
        ctx['signed_in'] = self.signed_in
        ctx['event'] = event
        ctx['series'] = event.get_course()[0] if len(event.get_course()) else None
        ctx['slug'] = kwargs['object'].slug
        ctx['video_page_slug'] = event.get_past_event_recording_slug()

        full_transcript = self.request.GET.get('fullTranscript')
        ctx['full_transcript'] = full_transcript

        if full_transcript:
            bespoke_breadcrumbs = [
                {
                    'title': 'Back',
                    'url': reverse(
                        'export_academy:video-on-demand', kwargs={'slug': event.get_past_event_recording_slug()}
                    ),
                },
            ]
        else:
            bespoke_breadcrumbs = self.get_breadcrumbs

        ctx['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        return ctx
