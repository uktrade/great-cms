from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from core.blocks import BasicTopicCardBlock, ColumnsBlock
from core.models import CMSGenericPage
from domestic.models import BaseContentPage
from international_investment.core.helpers import (
    get_investment_opportunities_search_filters,
)
from international_investment.forms import InvestmentOpportunitiesSearchForm


class InvestmentIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = [
        'international_investment.InvestmentSectorsPage',
        'international_investment.InvestmentRegionsPage',
        'international_investment.InvestmentOpportunityArticlePage',
    ]
    template = 'investment/index.html'

    def serve(self, request, *args, **kwargs):
        # Get filter parameters from GET request or kwargs
        sector = request.GET.getlist('sector', kwargs.get('sector', []))
        region = request.GET.getlist('region', kwargs.get('region', []))
        investment_type = request.GET.getlist('investment_type', kwargs.get('investment_type', []))

        # Simulate POST by filling in POST data
        request.POST = request.POST.copy()
        request.POST.setlist('sector', sector)
        request.POST.setlist('region', region)
        request.POST.setlist('investment_type', investment_type)
        request.method = 'POST'  # Simulate POST method

        # Initialize form with initial data
        form = InvestmentOpportunitiesSearchForm(
            request.POST,
            initial={
                'sector': sector,
                'region': region,
                'investment_type': investment_type,
            },
        )

        # Get filter choices from the opportunities
        opportunities = InvestmentOpportunityArticlePage.objects.live()
        sector_choices, region_choices, investment_type_choices = get_investment_opportunities_search_filters(
            opportunities
        )
        form.fields['sector'].choices = sector_choices
        form.fields['region'].choices = region_choices
        form.fields['investment_type'].choices = investment_type_choices

        # Filter opportunities based on selected filters
        if sector:
            opportunities = opportunities.filter(sector__in=sector)
        if region:
            opportunities = opportunities.filter(region__in=region)
        if investment_type:
            opportunities = opportunities.filter(investment_type__in=investment_type)

        # Paginate results
        paginator = Paginator(opportunities, 10)
        page = request.GET.get('page', 1)
        opportunities = paginator.get_page(page)

        # Set breadcrumbs and render the page
        breadcrumbs = [{'name': 'Home', 'url': '/international/'}]
        return render(
            request,
            'investment/index.html',
            {
                'form': form,
                'page': self,
                'results': opportunities,
                'pagination': opportunities,
                'page_range': paginator.get_elided_page_range(number=opportunities.number),
                'breadcrumbs': breadcrumbs,
            },
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        self.set_ga360_payload(
            page_id='Index',
            business_unit='Investment',
            site_section='investment',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]

        opportunities = InvestmentOpportunityArticlePage.objects.live()

        sector_filters = []
        investment_type_filters = []
        region_filters = []

        for opportunity in opportunities:
            if opportunity.sector not in sector_filters:
                sector_filters.append(opportunity.sector)
            if opportunity.region not in region_filters:
                region_filters.append(opportunity.region)
            if opportunity.investment_type not in investment_type_filters:
                investment_type_filters.append(opportunity.investment_type)

        context.update(
            breadcrumbs=breadcrumbs,
            sector_filters=sector_filters,
            investment_type_filters=investment_type_filters,
            region_filters=region_filters,
            results=opportunities,
        )
        return context


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


class InvestmentOpportunityArticlePage(BaseContentPage):
    parent_page_types = [
        'international_investment.InvestmentIndexPage',
    ]
    subpage_types = []
    template = 'investment/opportunity_article.html'

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

    region = models.TextField()
    location = models.TextField()
    sector = models.TextField()
    investment_type = models.TextField()

    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        FieldPanel('article_image'),
        FieldPanel('article_body'),
        FieldPanel('article_case_studies'),
        FieldPanel('data_points'),
        FieldPanel('region'),
        FieldPanel('location'),
        FieldPanel('sector'),
        FieldPanel('investment_type'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        self.set_ga360_payload(
            page_id='OpportunityArticle',
            business_unit='Investment',
            site_section='Investment opportunity article',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        investment_opportunities_url = '/international/investment/'
        if request.GET.get('back'):
            investment_opportunities_url = request.get_full_path().split('back=', 1)[1]

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Investment opportunities', 'url': investment_opportunities_url},
        ]

        context.update(
            breadcrumbs=breadcrumbs,
        )
        return context
