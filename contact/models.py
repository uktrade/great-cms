from django.db import models
from django.forms import Select
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from core import snippet_slugs
from core.cms_panels import SearchEngineOptimisationPanel
from core.cms_snippets import NonPageContentSEOMixin, NonPageContentSnippetBase


@register_snippet
class ContactSuccessSnippet(
    NonPageContentSEOMixin,
    NonPageContentSnippetBase,
):

    slug_options = {
        # This limits the slugs and URL paths that can be configured for these snippets.
        # It follows a common pattern from the V1 site
        snippet_slugs.HELP_FORM_SUCCESS: {
            'title': 'Contact domestic form success',
            'page_path': '/contact/domestic/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_EVENTS: {
            'title': 'Contact Events form success',
            'page_path': '/contact/events/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_DSO: {
            'title': 'Contact Defence and Security Organisation form success',
            'page_path': ('/contact/defence-and-security-organisation/success/'),
        },
        snippet_slugs.HELP_FORM_SUCCESS_EXPORT_ADVICE: {
            'title': 'Contact exporting from the UK form success',
            'page_path': '/contact/export-advice/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_FEEDBACK: {
            'title': 'Contact feedback form success',
            'page_path': '/contact/feedback/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_FIND_COMPANIES: {
            'title': 'Contact find UK companies form success',
            'page_path': '/contact/find-uk-companies/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_INTERNATIONAL: {
            'title': 'Contact international form success',
            'page_path': '/contact/international/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_SOO: {
            'title': 'Contact Selling Online Overseas form success',
            'page_path': '/contact/selling-online-overseas/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_BEIS: {
            'title': 'Contact BEIS form success',
            'page_path': '/contact/department-for-business-energy-and-industrial-strategy/success/',
        },
        snippet_slugs.HELP_FORM_SUCCESS_DEFRA: {
            'title': 'Contact DEFRA form success',
            'page_path': '/contact/department-for-environment-food-and-rural-affairs/success/',
        },
    }

    # slug field comes from NonPageContentSnippetBase
    # internal_title field comes from NonPageContentSnippetBase

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
