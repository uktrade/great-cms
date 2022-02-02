from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from contact.views import (
    DefenceAndSecurityOrganisationFormView,
    DomesticEnquiriesFormView,
    DomesticFormView,
    DomesticSuccessView,
    EcommerceSupportFormPageView,
    EventsFormView,
    ExportingAdviceFormView,
    ExportSupportSuccessPageView,
    FeedbackFormView,
    GuidanceView,
    InternationalFormView,
    InternationalSuccessView,
    OfficeContactFormView,
    OfficeFinderFormView,
    OfficeSuccessView,
    RoutingFormView,
    SellingOnlineOverseasFormView,
    SellingOnlineOverseasSuccessView,
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
        'contact/triage/great-account/<slug:slug>/',
        skip_ga360(GuidanceView.as_view()),
        {
            'snippet_import_path': 'contact.models.ContactUsGuidanceSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-great-account-guidance',
    ),
    path(
        'contact/triage/export-opportunities/<slug:slug>/',
        skip_ga360(GuidanceView.as_view()),
        {
            'snippet_import_path': 'contact.models.ContactUsGuidanceSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-export-opportunities-guidance',
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
    path(
        'contact/feedback/',
        skip_ga360(FeedbackFormView.as_view()),
        name='contact-us-feedback',
    ),
    path(
        'contact/feedback/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_FEEDBACK,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-feedback-success',
    ),
    path(
        'contact/export-advice/',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-export-advice',
                kwargs={'step': 'comment'},
            )
        ),
        name='export-advice-routing-form',
    ),
    path(
        # Note: this was migrated from great-domestic-ui, but ExportingAdviceFormView
        # does not use it as its success view (and the messaging is the same anyway)
        'contact/export-advice/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_EXPORT_ADVICE,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-export-advice-success',
    ),
    path(
        # Has to come after the /success/ slug
        'contact/export-advice/<slug:step>/',
        skip_ga360(
            ExportingAdviceFormView.as_view(
                url_name='contact:contact-us-export-advice',
                done_step_name='finished',
            ),
        ),
        name='contact-us-export-advice',
    ),
    path(
        'contact/international/',
        skip_ga360(InternationalFormView.as_view()),
        name='contact-us-international',
    ),
    path(
        'contact/international/success/',
        skip_ga360(InternationalSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_INTERNATIONAL,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-international-success',
    ),
    path(
        'contact/selling-online-overseas/',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-soo',
                kwargs={'step': 'contact-details'},
            )
        ),
        name='contact-us-soo-redirect',
    ),
    path(
        'contact/selling-online-overseas/organisation/',
        QuerystringRedirectView.as_view(
            url=reverse_lazy(
                'contact:contact-us-soo',
                kwargs={'step': 'contact-details'},
            )
        ),
        name='contact-us-soo-organisation-redirect',
    ),
    path(
        'contact/selling-online-overseas/success/',
        skip_ga360(SellingOnlineOverseasSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS_SOO,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-selling-online-overseas-success',
    ),
    path(
        'contact/selling-online-overseas/<slug:step>/',
        login_required(
            skip_ga360(
                SellingOnlineOverseasFormView.as_view(
                    url_name='contact:contact-us-soo',
                    done_step_name='finished',
                )
            ),
            login_url=reverse_lazy('core:login'),
        ),
        name='contact-us-soo',
    ),
]
