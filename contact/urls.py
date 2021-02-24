from django.urls import path
from great_components.decorators import skip_ga360

from . import snippet_slugs
from .views import DomesticEnquiriesFormView, DomesticFormView, DomesticSuccessView

app_name = 'contact'

urlpatterns = [
    path(
        'domestic/',
        skip_ga360(DomesticFormView.as_view()),
        name='contact-us-domestic',
    ),
    path(
        'domestic/enquiries/',
        skip_ga360(DomesticEnquiriesFormView.as_view()),
        name='contact-us-enquiries',
    ),
    path(
        'domestic/success/',
        skip_ga360(DomesticSuccessView.as_view()),
        {
            'slug': snippet_slugs.HELP_FORM_SUCCESS,
            'snippet_import_path': 'contact.models.ContactSuccessSnippet',  # see core.mixins.GetSnippetContentMixin
        },
        name='contact-us-domestic-success',
    ),
]
