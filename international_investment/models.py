from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from core.blocks import BasicTopicCardBlock, ColumnsBlock
from core.models import CMSGenericPage
from domestic.models import BaseContentPage


class InvestmentIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = [
        'international_investment.InvestmentSectorsPage',
        'international_investment.InvestmentRegionsPage',
    ]
    template = 'investment/index.html'


class InvestmentSectorsPage(BaseContentPage):
    parent_page_types = [
        'international_investment.InvestmentIndexPage',
    ]
    subpage_types = [
        'international_investment.InvestmentArticlePage',
    ]
    template = 'investment/sectors.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        self.set_ga360_payload(
            page_id='Article',
            business_unit='Investment',
            site_section='Sectors',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]

        context.update(
            breadcrumbs=breadcrumbs,
        )
        return context


class InvestmentRegionsPage(BaseContentPage):
    parent_page_types = [
        'international_investment.InvestmentIndexPage',
    ]
    subpage_types = [
        'international_investment.InvestmentArticlePage',
    ]
    template = 'investment/regions.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        self.set_ga360_payload(
            page_id='Article',
            business_unit='Investment',
            site_section='Regions',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]

        context.update(
            breadcrumbs=breadcrumbs,
        )
        return context


class InvestmentArticlePage(BaseContentPage):
    parent_page_types = [
        'international_investment.InvestmentSectorsPage',
        'international_investment.InvestmentRegionsPage',
    ]
    subpage_types = []
    template = 'investment/article.html'

    article_title = models.TextField()
    article_subheading = StreamField(
        [
            (
                'text',
                RichTextBlock(),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )
    article_teaser = models.TextField(
        blank=True,
        null=True,
        help_text='This is a subheading that displays when the article is featured on another page',
    )
    article_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    article_body = StreamField(
        [
            (
                'text',
                RichTextBlock(),
            ),
            ('image', ImageChooserBlock(required=False, template='core/includes/_article_image.html')),
            (
                'Columns',
                StreamBlock(
                    [
                        ('column', ColumnsBlock()),
                    ],
                    help_text='Add two or three columns text',
                    min_num=2,
                    max_num=3,
                    template='core/includes/_columns.html',
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )
    article_case_studies = StreamField(
        [
            (
                'text',
                RichTextBlock(),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    data_points = StreamField(
        [
            (
                'points',
                StreamBlock(
                    [
                        ('data_point', BasicTopicCardBlock()),
                    ],
                    block_counts={
                        'data_point': {'min_num': 1},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        FieldPanel('article_image'),
        FieldPanel('article_body'),
        FieldPanel('article_case_studies'),
        FieldPanel('data_points'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        self.set_ga360_payload(
            page_id='Article',
            business_unit='Investment',
            site_section='Investment article',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        parent_page_name = self.get_parent().title

        parent_page_url = request.get_full_path().rstrip('/')

        # Split by slash and remove the last segment
        parent_directory = '/'.join(parent_page_url.split('/')[:-1]) + '/'

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': parent_page_name, 'url': parent_directory},
        ]

        context.update(
            breadcrumbs=breadcrumbs,
        )
        return context
