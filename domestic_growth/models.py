import pickle

from django.db import models

from domestic_growth import (
    cms_panels,
    helpers,
)
from wagtail import blocks
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtailseo.models import SeoMixin
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.search import index
from wagtail.admin.panels import (
    FieldPanel,
)
from wagtail.snippets.models import register_snippet

from domestic_growth.blocks import DomesticGrowthCardBlock


class DomesticGrowthLandingPage(SeoMixin, cms_panels.DomesticGrowthLandingPagePanels, Page):
    template = 'landing.html'

    class Meta:
        verbose_name = 'Domestic Growth Landing page'

    hero_title = models.TextField(
        null=True,
    )

    hero_body = StreamField(
        [
            (
                'hero_cards',
                StreamBlock(
                    [
                        ('hero_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'hero_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    support_title = models.TextField(
        null=True,
    )

    support_body = StreamField(
        [
            (
                'support_cards',
                StreamBlock(
                    [
                        ('support_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'support_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    popular_title = models.TextField(
        null=True,
    )

    popular_body = StreamField(
        [
            (
                'popular_cards',
                StreamBlock(
                    [
                        ('popular_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'popular_card': {'min_num': 3},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    news_title = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthLandingPage, self).get_context(request)
        context['news'] = helpers.get_dbt_news_articles()
        return context


class DomesticGrowthResultsPage(SeoMixin, cms_panels.DomesticGrowthResultsPagePanels, Page):
    template = 'results.html'

    class Meta:
        verbose_name = 'Domestic Growth Results page'

    subpage_types = ['domestic_growth.DomesticGrowthChildResultsPage']

    body = StreamField(
        [
            (
                'growth_hub',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                    ],
                ),
            ),
            (
                'chamber_of_commerce',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                    ],
                ),
            ),
            (
                'trade_associations',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                    ],
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthResultsPage, self).get_context(request)

        form_data = {}
        dynamic_data = None

        if request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(request.session.get('domestic_growth_triage_data')))[0]
            dynamic_data = helpers.get_nearest_by_postcode(form_data.get('postcode'))
        elif request.GET.get('postcode') and request.GET.get('sector'):
            form_data = {
                'postcode': request.GET.get('postcode'),
                'sector': request.GET.get('sector'),
            }
            dynamic_data = helpers.get_nearest_by_postcode(form_data.get('postcode'))

        context['session_data'] = form_data
        context['growth_hub'] = dynamic_data['growth_hub']
        context['chamber_of_commerce'] = dynamic_data['chamber_of_commerce']
        context['qs'] = '?postcode=' + request.GET.get('postcode') + '&sector=' + request.GET.get('sector')
        context['trade_associations'] = [
            {
                'name': 'Generic Trade Assocation name',
                'description': 'More info about generic trade association',
                'url': 'www.tradeassociation.com',
            }
        ]

        return context


class DomesticGrowthChildResultsPage(SeoMixin, cms_panels.DomesticGrowthResultsPagePanels, Page):
    template = 'results-child.html'

    class Meta:
        verbose_name = 'Domestic Growth Child Results page'

    parent_page_types = [
        'domestic_growth.DomesticGrowthResultsPage',
    ]

    body = StreamField(
        [
            (
                'section',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                        (
                            'content',
                            blocks.ListBlock(
                                SnippetChooserBlock('domestic_growth.DomesticGrowthContent'),
                                label='Choose content snippet',
                            ),
                        ),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthChildResultsPage, self).get_context(request)

        form_data = {}

        if request.session.get('domestic_growth_triage_data'):
            form_data = pickle.loads(bytes.fromhex(request.session.get('domestic_growth_triage_data')))[0]
        elif request.GET.get('postcode') and request.GET.get('sector'):
            form_data = {
                'postcode': request.GET.get('postcode'),
                'sector': request.GET.get('sector'),
            }

        context['session_data'] = form_data
        context['qs'] = '?postcode=' + request.GET.get('postcode') + '&sector=' + request.GET.get('sector')
        context['ukea_events'] = [
            {
                'name': 'Sector based UKEA Event',
                'url': 'www.ukea.com',
            }
        ]

        return context


@register_snippet
class DomesticGrowthContent(index.Indexed, models.Model):
    content_id = models.CharField(blank=True)
    title = models.CharField()
    description = models.TextField()
    link_text = models.CharField(blank=True)
    url = models.CharField(blank=True)
    sector = models.CharField(blank=True)
    is_dynamic = models.BooleanField(default=False)

    panels = [
        FieldPanel('content_id'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('link_text'),
        FieldPanel('url'),
        FieldPanel('sector'),
        FieldPanel('is_dynamic'),
    ]

    search_fields = [
        index.AutocompleteField('title'),
    ]

    class Meta:
        ordering = ('title',)

    def __str__(self):
        if self.is_dynamic:
            return self.title + ' (***** Dynamic *****)'

        return self.title
