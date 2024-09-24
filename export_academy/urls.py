from django.contrib.auth.decorators import login_required
from django.urls import path

from core import snippet_slugs
from core.urls import SIGNUP_URL
from export_academy import views
from export_academy.helpers import check_registration

app_name = 'export_academy'


urlpatterns = [
    path(
        'events/',
        (views.EventListView.as_view()),
        {
            'slug': snippet_slugs.EXPORT_ACADEMY_LISTING_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='upcoming-events',
    ),
    path(
        'events/<slug:slug>/',
        views.EventsDetailsView.as_view(),
        name='event-details',
    ),
    path(
        'registration/<uuid:event_id>',
        login_required(views.RegistrationPersonalDetails.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration',
    ),
    path(
        'registration/details/',
        login_required(views.RegistrationPersonalDetails.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-details',
    ),
    path(
        'registration/details/edit/',
        login_required(views.RegistrationPersonalDetails.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
            'edit': True,
        },
        name='registration-details-edit',
    ),
    path(
        'registration/experience/',
        login_required(views.RegistrationExportExperience.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-experience',
    ),
    path(
        'registration/experience/edit/',
        login_required(views.RegistrationExportExperience.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
            'edit': True,
        },
        name='registration-experience-edit',
    ),
    path(
        'registration/business/',
        login_required(views.RegistrationBusinessDetails.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-business',
    ),
    path(
        'registration/business/edit/',
        login_required(views.RegistrationBusinessDetails.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
            'edit': True,
        },
        name='registration-business-edit',
    ),
    path(
        'registration/finally/',
        login_required(views.RegistrationMarketingSources.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-marketing',
    ),
    path(
        'registration/finally/edit/',
        login_required(views.RegistrationMarketingSources.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
            'edit': True,
        },
        name='registration-marketing-edit',
    ),
    path(
        'registration/confirm/',
        login_required(views.RegistrationConfirmChoices.as_view(), login_url=SIGNUP_URL),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-confirm',
    ),
    path('booking/', check_registration(views.BookingUpdateView.as_view()), name='booking'),
    path(
        'registration/booking/<uuid:booking_id>/success/',
        views.SuccessPageView.as_view(template_name='export_academy/booking_success.html'),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-success',
    ),
    path(
        'registration/success/',
        views.SuccessPageView.as_view(template_name='export_academy/booking_success.html'),
        {
            'slug': snippet_slugs.EA_REGISTRATION_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='registration-edit-success',
    ),
    path(
        'booking/<uuid:booking_id>/success/',
        views.SuccessPageView.as_view(template_name='export_academy/booking_success.html'),
        {
            'slug': snippet_slugs.EXPORT_ACADEMY_LISTING_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='booking-success',
    ),
    path(
        'booking/<uuid:booking_id>/cancellation/success',
        views.SuccessPageView.as_view(template_name='export_academy/booking_success.html'),
        {
            'slug': snippet_slugs.EXPORT_ACADEMY_LISTING_PAGE_HERO,
            'snippet_import_path': 'core.models.HeroSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='cancellation-success',
    ),
    path(
        'event/<uuid:pk>/',
        views.EventVideoView.as_view(),
        name='event-video',
    ),
    path(
        'calendar/',
        views.DownloadCalendarView.as_view(),
        name='calendar',
    ),
    path(
        '<slug:slug>/',
        views.EACourseView.as_view(),
        name='course',
    ),
    path(
        'event-recordings/<slug:slug>/',
        views.EventVideoOnDemandView.as_view(),
        name='video-on-demand',
    ),
    path('event/join/<uuid:event_id>', views.JoinBookingView.as_view(), name='join'),
    path('signup', views.SignUpView.as_view(), name='signup'),
    path('signup/verification', views.VerificationCodeView.as_view(), name='signup-verification'),
    path('signup/complete', views.SignUpCompleteView.as_view(), name='signup-complete'),
    path('signin', views.SignInView.as_view(), name='signin'),
]
