from django.db import models
from django.forms import Select
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.snippets.models import register_snippet

from core import snippet_slugs
from core.cms_snippets import NonPageContentSEOMixin, NonPageContentSnippetBase


class ContactUsGuidanceSnippet(
    NonPageContentSEOMixin,
    NonPageContentSnippetBase,
):
    """Rendered content displayed as part of a contact-us journey, such as a
    description of what action to take, to pre-empt the need to send a message."""

    slug_options = {
        # This limits the slugs and URL paths that can be configured for these snippets.
        # It follows a common pattern from the V1 site
        # (Note that page_path is functionally redundant, but helps us map to real URLs
        # if we need to trace through where content goes)
        snippet_slugs.HELP_EXOPP_ALERTS_IRRELEVANT: {
            'title': 'Guidance - Daily alerts are not relevant',
            'page_path': ('/contact/triage/export-opportunities/alerts-not-relevant/'),
        },
        snippet_slugs.HELP_EXOPPS_NO_RESPONSE: {
            'title': 'Guidance - Export Opportunity application no response',
            'page_path': ('/contact/triage/export-opportunities/opportunity-no-response/'),
        },
        snippet_slugs.HELP_MISSING_VERIFY_EMAIL: {
            'title': 'Guidance - Email verification missing',
            'page_path': ('/contact/triage/great-account/no-verification-email/'),
        },
        snippet_slugs.HELP_PASSWORD_RESET: {
            'title': 'Guidance - Missing password reset link',
            'page_path': ('/contact/triage/great-account/password-reset/'),
        },
        snippet_slugs.HELP_COMPANIES_HOUSE_LOGIN: {
            'title': 'Guidance - Companies House login not working',
            'page_path': ('/contact/triage/great-account/companies-house-login/'),
        },
        snippet_slugs.HELP_VERIFICATION_CODE_ENTER: {
            'title': 'Guidance - Where to enter letter verification code',
            'page_path': ('/contact/triage/great-account/verification-letter-code/'),
        },
        snippet_slugs.HELP_VERIFICATION_CODE_LETTER: {
            'title': 'Guidance - Verification letter not delivered',
            'page_path': ('/contact/triage/great-account/no-verification-letter/'),
        },
        snippet_slugs.HELP_VERIFICATION_CODE_MISSING: {
            'title': 'Guidance - Verification code not delivered',
            'page_path': ('/contact/triage/great-account/verification-missing/'),
        },
        snippet_slugs.HELP_ACCOUNT_COMPANY_NOT_FOUND: {
            'title': 'Guidance - Company not found',
            'page_path': ('/contact/triage/great-account/company-not-found/'),
        },
        snippet_slugs.HELP_EXPORTING_TO_UK: {
            # NB snippet_slugs.HELP_EXPORTING_TO_UK is NOT bootstrapped via data migration
            'title': 'Guidance - Exporting to the UK',
            'page_path': ('contact/triage/international/exporting-to-the-uk/'),
        },
    }

    title = models.CharField(
        max_length=255,
        verbose_name='heading',
    )

    body = RichTextField(
        verbose_name='Body content',
        blank=False,
    )

    panels = [
        MultiFieldPanel(
            heading='Purpose',
            children=[
                FieldPanel('slug', widget=Select),
            ],
        ),
        MultiFieldPanel(
            heading='Page content',
            children=[
                FieldPanel('title'),
                FieldPanel('body'),
            ],
        ),
    ]

    def __str__(self):
        return f'Contact Us Guidance Snippet: {self.internal_title}'


@register_snippet
class ContactSuccessSnippet(
    NonPageContentSEOMixin,
    NonPageContentSnippetBase,
):
    """CMS-editable content that will be inserted into a Django-owned 'success' page
    for the selected post-submission success page

    For use of these snippets, see core.mixins.GetSnippetContentMixin
    """

    slug_options = {
        # This limits the slugs and URL paths that can be configured for these snippets.
        # It follows a common pattern from the V1 site
        # (Note that page_path is functionally redundant, but helps us map to real URLs
        # if we need to trace through where content goes)
        snippet_slugs.HELP_FORM_SUCCESS: {
            'title': 'Contact domestic form success page content',
            'page_path': '/contact/domestic/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_EVENTS: {
            'title': 'Contact Events form success page content',
            'page_path': '/contact/events/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_DSO: {
            'title': 'Contact Defence and Security Organisation form success page content',
            'page_path': ('/contact/defence-and-security-organisation/success/'),
        },
        snippet_slugs.HELP_FORM_SUCCESS_EXPORT_ADVICE: {
            'title': 'Contact exporting from the UK form success page content',
            'page_path': '/contact/export-advice/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_FEEDBACK: {
            'title': 'Contact feedback form success page content',
            'page_path': '/contact/feedback/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_FIND_COMPANIES: {
            'title': 'Contact find UK companies form success page content',
            'page_path': '/contact/find-uk-companies/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_INTERNATIONAL: {
            'title': 'Contact international form success page content',
            'page_path': '/contact/international/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_SOO: {
            'title': 'Contact Selling Online Overseas form success page content',
            'page_path': '/contact/selling-online-overseas/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_BEIS: {
            'title': 'Contact BEIS form success page content',
            'page_path': '/contact/department-for-business-energy-and-industrial-strategy/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_DEFRA: {
            'title': 'Contact DEFRA form success page content',
            'page_path': '/contact/department-for-environment-food-and-rural-affairs/success/',
        },
    }

    # slug field comes from NonPageContentSnippetBase
    # internal_title field comes from NonPageContentSnippetBase

    breadcrumbs_label = models.CharField(
        max_length=50,
    )
    heading = models.CharField(
        max_length=255,
        verbose_name='Title',
    )
    body_text = models.CharField(
        max_length=255,
        verbose_name='Body text',
    )
    next_title = models.CharField(
        max_length=255,
        verbose_name='Next title',
    )
    next_body_text = models.CharField(
        max_length=255,
        verbose_name='Next body text',
    )

    panels = [
        MultiFieldPanel(
            heading='Purpose',
            children=[
                FieldPanel('slug', widget=Select),
            ],
        ),
        MultiFieldPanel(
            heading='breadcrumbs',
            children=[
                FieldPanel('breadcrumbs_label'),
            ],
        ),
        MultiFieldPanel(
            heading='heading',
            children=[
                FieldPanel('heading'),
                FieldPanel('body_text'),
            ],
        ),
        MultiFieldPanel(
            heading='Next steps',
            children=[
                FieldPanel('next_title'),
                FieldPanel('next_body_text'),
            ],
        ),
    ]

    def __str__(self):
        return f'Contact Success Snippet: {self.internal_title}'
