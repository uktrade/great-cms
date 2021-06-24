from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from contact.views import (
    DefenceAndSecurityOrganisationFormView,
    DomesticEnquiriesFormView,
    DomesticFormView,
    DomesticSuccessView,
    EcommerceSupportFormPageView,
    EventsFormView,
    ExportSupportSuccessPageView,
    GuidanceView,
    OfficeContactFormView,
    OfficeFinderFormView,
    OfficeSuccessView,
    RoutingFormView,
)
from core import snippet_slugs
from core.views import QuerystringRedirectView

app_name = 'contact'
# NB: when reverse()ing a named URL listed below, remember to prepend it with `contact:`

# NB: the paths here are all starting from the root of '/', not '/contact/'...
urlpatterns = [
    path(
        'contact/',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-routing-form',
                kwargs={'step': 'location'},
            ),
        ),
        name='contact-us-routing-form-redirect',
    ),
    path(
        'contact/triage/<slug:step>/',
        skip_ga360(
            RoutingFormView.as_view(
                url_name='contact:contact-us-routing-form',
                done_step_name='finished',
            )
        ),
        name='contact-us-routing-form',
    ),
    path(
        'contact/triage/great-account/<slug:slug>/',
        skip_ga360(GuidanceView.as_view()),
        {
            'snippet_import_path': 'contact.models.ContactUsGuidanceSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-great-account-guidance',
    ),
    path(
        'contact/domestic/',
        skip_ga360(DomesticFormView.as_view()),
        name='contact-us-domestic',
    ),
    path(
        'contact/domestic/enquiries/',
        skip_ga360(DomesticEnquiriesFormView.as_view()),
        name='contact-us-enquiries',
    ),
    path(
        'contact/domestic/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-domestic-success',
    ),
    # The following are views served by the contact app but which are NOT prefixed '/contact/'
    path(
        'campaigns/ecommerce-export-support/apply/',
        EcommerceSupportFormPageView.as_view(),
        name='ecommerce-export-support-form',
    ),
    path(
        'campaigns/ecommerce-export-support/success/',
        skip_ga360(ExportSupportSuccessPageView.as_view()),
        name='ecommerce-export-support-success',
    ),
    path('contact/office-finder/', skip_ga360(OfficeFinderFormView.as_view()), name='office-finder'),
    path(
        'contact/office-finder/<str:postcode>/',
        skip_ga360(OfficeContactFormView.as_view()),
        name='office-finder-contact',
    ),
    path(
        'contact/office-finder/<str:postcode>/success/',
        skip_ga360(OfficeSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-office-success',
    ),
    path(
        'contact/events/',
        skip_ga360(EventsFormView.as_view()),
        name='contact-us-events-form',
    ),
    path(
        'contact/events/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_EVENTS,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-events-success',
    ),
    path(
        'contact/defence-and-security-organisation/',
        skip_ga360(DefenceAndSecurityOrganisationFormView.as_view()),
        name='contact-us-dso-form',
    ),
    path(
        'contact/defence-and-security-organisation/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_DSO,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-dso-success',
    ),
]
