from django.db import models
from django.forms import Select
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.snippets.models import register_snippet

from core import snippet_slugs
from core.cms_panels import SearchEngineOptimisationPanel
from core.cms_snippets import NonPageContentSEOMixin, NonPageContentSnippetBase


@register_snippet
class ContactPageContentSnippet(
    NonPageContentSEOMixin,
    NonPageContentSnippetBase,
):
    """CMS-editable content that will be inserted into a Django-owned page that also
    renders (and handles submission of) a Form of some kind (defined by the Django view)

    For use of these snippets, see core.mixins.GetSnippetContentMixin
    """

    slug_options = {
        # This limits the slugs and URL paths that can be configured for these snippets.
        # It follows a common pattern from the V1 site
        snippet_slugs.EUEXIT_DOMESTIC_FORM: {
            'title': 'Transition Period form supporting content',
            'page_path': '/transition-period/contact/',
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
    body_text = RichTextField(
        max_length=255,
        verbose_name='Body content',
    )
    submit_button_text = models.CharField(
        max_length=255,
        verbose_name='Submit button text',
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
            heading='Page content',
            children=[
                FieldPanel('heading'),
                FieldPanel('body_text'),
                FieldPanel('submit_button_text'),
            ],
        ),
        SearchEngineOptimisationPanel(),
    ]

    def __str__(self):
        return f'Contact Page Content Snippet: {self.internal_title}'


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
        snippet_slugs.EUEXIT_FORM_SUCCESS: {
            'title': 'Transition Period form success page content',
            'page_path': '/transition-period/contact/',
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
        SearchEngineOptimisationPanel(),
    ]

    def __str__(self):
        return f'Contact Success Snippet: {self.internal_title}'
