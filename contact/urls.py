from django.urls import path
from great_components.decorators import skip_ga360

from core import snippet_slugs
from .views import (
    DomesticEnquiriesFormView,
    DomesticFormView,
    DomesticSuccessView,
    EcommerceSupportFormPageView,
    ExportSupportSuccessPageView,
    GuidanceView,
    RoutingFormView,
)

app_name = 'contact'
# NB: when reverse()ing a named URL listed below, remember to prepend it with `contact:`

urlpatterns = [
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
]
