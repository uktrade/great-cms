from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey
from taggit.models import TagBase, TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtailcache.cache import WagtailCacheMixin

from core.blocks import ColumnsBlock
from core.mixins import HCSATNonFormPageMixin
from core.models import CMSGenericPage, TimeStampedModel
from domestic.models import BaseContentPage
from international_online_offer import services
from international_online_offer.core import (
    choices,
    filter_tags,
    helpers,
    professions,
    region_sector_helpers,
    regions,
)
from international_online_offer.forms import LocationSelectForm, WagtailAdminDBTSectors
from international_online_offer.services import get_median_salaries, get_rent_data
from .helpers import get_step_guide_accordion_items


class EYBIndexPage(BaseContentPage):
    parent_page_types = [
        'international.GreatInternationalHomePage',
    ]
    subpage_types = [
        'international_online_offer.EYBGuidePage',
    ]
    template = 'eyb/index.html'

    def serve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/international/expand-your-business-in-the-uk/guide/')

        breadcrumbs = [{'name': 'Home', 'url': '/international/'}]
        return render(
            request,
            'eyb/index.html',
            {
                'page': self,
                'breadcrumbs': breadcrumbs,
            },
        )


def get_triage_data_for_user(request):
    try:
        return TriageData.objects.get(hashed_uuid=request.user.hashed_uuid)
    except AttributeError:
        return None
    except TriageData.DoesNotExist:
        return None


def get_user_data_for_user(request):
    try:
        return UserData.objects.get(hashed_uuid=request.user.hashed_uuid)
    except AttributeError:
        return None
    except UserData.DoesNotExist:
        return None


class EYBHCSAT(HCSATNonFormPageMixin):
    hcsat_service_name = 'eyb'
    is_international_hcsat = True


class EYBGuidePage(WagtailCacheMixin, BaseContentPage, EYBHCSAT):
    parent_page_types = ['international_online_offer.EYBIndexPage']
    subpage_types = [
        'international_online_offer.EYBArticlePage',
        'international_online_offer.EYBTradeShowsPage',
        'international_online_offer.EYBArticlesPage',
    ]
    template = 'eyb/guide.html'

    def serve(self, request, *args, **kwargs):
        # hcsat
        if request.method == 'POST':
            return self.post(request)

        user_data = get_user_data_for_user(request)
        triage_data = get_triage_data_for_user(request)

        # Determine the current step view name
        if not request.user.is_superuser:
            current_step_view = helpers.get_current_step(user_data, triage_data)
            if current_step_view:
                response = redirect(f'international_online_offer:{current_step_view}')
                if request.GET.get('login'):
                    response['Location'] += '?resume=true'
                return response

        context = self.get_context(request, user_data=user_data, triage_data=triage_data)

        context = {
            **context,
            'market_data': {
                'select': {
                    'label': {'text': 'Data for'},
                    'items': [
                        {'value': 'uk', 'text': 'United Kingdom'},
                        {'value': 'bar', 'text': 'Bar'},
                        {'value': 'baz', 'text': 'Baz'},
                    ],
                },
                'figures': [
                    {
                        'icon_path': 'svg/icon-planning.svg',
                        'value': 117830,
                        'description': 'businesses in this sector',
                    },
                    {
                        'icon_path': 'svg/icon-planning.svg',
                        'value': 1342100,
                        'description': 'employees in this sector',
                    },
                ],
                'data_year': '1979',
                'data_source': 'Inter-Departmental Business Register, Office for National Statistics',
            },
            'salary_data': {
                'select': {
                    'label': {'text': 'Average annual salary data for'},
                    'items': [
                        {'value': 'uk', 'text': 'United Kingdom'},
                        {'value': 'bar', 'text': 'Bar'},
                        {'value': 'baz', 'text': 'Baz'},
                    ],
                },
                'figures': [
                    {
                        'icon_path': 'svg/icon-planning.svg',
                        'prefix': '£',
                        'value': 16018,
                        'description': 'For professions like IT user support, '
                        'IT operations technicians and electricians',
                    },
                    {
                        'icon_path': 'svg/icon-planning.svg',
                        'prefix': '£',
                        'value': 20404,
                        'description': 'For professions like electronic engineers and IT project managers',
                    },
                    {
                        'icon_path': 'svg/icon-planning.svg',
                        'prefix': '£',
                        'value': 39397,
                        'description': 'For professions like senior restaurant '
                        'manager and food company chief executive.',
                    },
                ],
                'data_year': '1979',
                'data_source': 'Inter-Departmental Business Register, Office for National Statistics',
            },
            'rent_data': {
                'select': {
                    'label': {'text': 'Average rent data for'},
                    'items': [
                        {'value': 'uk', 'text': 'United Kingdom'},
                        {'value': 'bar', 'text': 'Bar'},
                        {'value': 'baz', 'text': 'Baz'},
                    ],
                },
                'tabs': [
                    {
                        'id': 'large-warehouse',
                        'label': 'Large warehouse',
                        'panel': {
                            'html': render_to_string(
                                'eyb/includes/dynamic-guide/tab_content.html',
                                {
                                    'title': 'Large warehouse',
                                    'value_from': 12345,
                                    'value_to': 4321,
                                },
                            )
                        },
                    },
                    {
                        'id': 'small-warehouse',
                        'label': 'Small warehouse',
                        'panel': {
                            'html': render_to_string(
                                'eyb/includes/dynamic-guide/tab_content.html',
                                {
                                    'title': 'Small warehouse',
                                    'value_from': 22334455,
                                    'value_to': 55443322,
                                },
                            )
                        },
                    },
                    {
                        'id': 'shopping-centre',
                        'label': 'Shopping centre',
                        'panel': {
                            'html': render_to_string(
                                'eyb/includes/dynamic-guide/tab_content.html',
                                {
                                    'title': 'Shopping centre',
                                    'value_from': 333777,
                                    'value_to': 777333,
                                },
                            )
                        },
                    },
                    {
                        'id': 'high-street-retail',
                        'label': 'High street retail',
                        'panel': {
                            'html': render_to_string(
                                'eyb/includes/dynamic-guide/tab_content.html',
                                {
                                    'title': 'High street retail',
                                    'value_from': 333777,
                                    'value_to': 777333,
                                },
                            )
                        },
                    },
                    {
                        'id': 'work-office',
                        'label': 'Work office',
                        'panel': {
                            'html': render_to_string(
                                'eyb/includes/dynamic-guide/tab_content.html',
                                {
                                    'title': 'Work office',
                                    'value_from': 333777,
                                    'value_to': 777333,
                                },
                            )
                        },
                    },
                ],
            },
        }

        return TemplateResponse(
            request, 'eyb/guide-dynamic.html' if ('dynamic' in request.GET) else self.template, context
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        context['accordion'] = get_step_guide_accordion_items()

        """
            Accept user_data and triage_data via kwargs to avoid multiple db calls.
            not using positional arguments as hcsat form invalid calls get_context
            and we want to keep the implementation of hcsat as generic as possible.
        """
        if 'user_data' not in kwargs:
            user_data = get_user_data_for_user(request)
        else:
            user_data = kwargs['user_data']

        if 'triage_data' not in kwargs:
            triage_data = get_triage_data_for_user(request)
        else:
            triage_data = kwargs['triage_data']

        bci_data = None
        if triage_data and triage_data.sector:
            bci_data = services.get_bci_data_by_dbt_sector(triage_data.sector, [regions.GB_GEO_CODE])

        # Get trade shows page (should only be one, is a parent / container page for all trade show pages)
        trade_shows_page = EYBTradeShowsPage.objects.live().filter().first()

        """
            Surface articles that have been tagged with the user's sector and their intent.
            I.e. each article needs two tags to display, for example, 'Food and drink',
            and 'Set up a new distribution centre'.
        """
        all_articles_tagged_with_sector_and_intent = []

        if triage_data and triage_data.sector and triage_data.intent:
            """
            Wagtail doesn't allow commas in tags and we need to match the sector
            'Agriculture, horticulture, fisheries and pets' i.e. below will match the tag
            'Agriculture horticulture fisheries and pets'
            """
            user_sector_no_commas = triage_data.sector.replace(',', '')

            # display articles based on free text tags
            all_articles_tagged_with_sector_and_intent = (
                EYBArticlePage.objects.live()
                .filter(tags__name__iexact=user_sector_no_commas)
                .filter(tags__name__in=triage_data.intent)
            )

            # include articles based on user sector and article's dbt sector not including any duplicates
            all_articles_tagged_with_sector_and_intent = all_articles_tagged_with_sector_and_intent.union(
                EYBArticlePage.objects.live().filter(dbt_sectors__contains=[triage_data.sector])
            )

        # Get any EYB articles that have been tagged with FINANCE_AND_SUPPORT
        all_articles_tagged_with_finance_and_support = EYBArticlePage.objects.live().filter(
            tags__name=filter_tags.FINANCE_AND_SUPPORT
        )

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
        ]

        context.update(
            complete_contact_form_link='international_online_offer:signup',
            complete_contact_form_link_text='Sign up',
            triage_data=triage_data,
            user_data=user_data,
            bci_data=bci_data[0] if bci_data and len(bci_data) > 0 else None,
            get_to_know_market_articles=all_articles_tagged_with_sector_and_intent,
            finance_and_support_articles=all_articles_tagged_with_finance_and_support,
            trade_shows_page=trade_shows_page,
            breadcrumbs=breadcrumbs,
        )

        self.set_ga360_payload(
            page_id='Guide',
            business_unit='ExpandYourBusiness',
            site_section='guide',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        self.set_csat_and_stage(request, context, self.hcsat_service_name, self.get_csat_form)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        self.set_is_csat_complete(request, context)

        return context


class EYBArticleTag(TagBase):
    """EYB article tag for filtering out content based on triage answers."""

    class Meta:
        verbose_name = 'EYB article tag for link to triage answer'
        verbose_name_plural = 'EYB article tags for links to triage answers'


class EYBArticlePageTag(TaggedItemBase):
    tag = models.ForeignKey(EYBArticleTag, related_name='ioo_tagged_articles', on_delete=models.CASCADE)
    content_object = ParentalKey('international_online_offer.EYBArticlePage', related_name='ioo_article_tagged_items')


class EYBArticlePage(BaseContentPage, EYBHCSAT):
    parent_page_types = [
        'international_online_offer.EYBGuidePage',
        'international_online_offer.EYBArticlesPage',
    ]
    subpage_types = []
    template = 'eyb/article.html'
    base_form_class = WagtailAdminDBTSectors
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
    dbt_sectors = ArrayField(
        models.CharField(),
        blank=True,
        default=list,
        help_text='Select multiple sectors by holding the Ctrl key (Windows) or the Command key (Mac). Currently the parent sector only is used for mapping.',  # noqa:E501
    )
    tags = ClusterTaggableManager(
        through=EYBArticlePageTag,
        blank=True,
        verbose_name='Article Tags',
        help_text="A comma-separated list of tags. Each article needs at least two tags to display a) a sector, b) an intent. Do not include commas in the sector name, e.g. 'Agriculture, horticulture, fisheries and pets' is tagged as 'Agriculture horticulture fisheries and pets'",  # noqa:E501
    )
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        FieldPanel('article_image'),
        FieldPanel('article_body'),
        FieldPanel('dbt_sectors'),
        FieldPanel('tags'),
    ]

    def serve(self, request, *args, **kwargs):
        # hcsat
        if request.method == 'POST':
            return self.post(request)
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        if helpers.is_authenticated(request):
            triage_data = get_triage_data_for_user(request)

            tags = self.tags.all()
            show_salary_component = helpers.can_show_salary_component(tags)
            show_rent_component = helpers.can_show_rent_component(tags)

            if triage_data:
                location = request.GET.get(
                    'location', triage_data.location if triage_data.location else choices.regions.LONDON
                )
                region = helpers.get_salary_region_from_region(location)

                median_salaries = get_median_salaries(triage_data.sector, geo_region=region)
                cleaned_median_salaries = helpers.clean_salary_data(median_salaries)

                (
                    large_warehouse_rent,
                    small_warehouse_rent,
                    shopping_centre,
                    high_street_retail,
                    work_office,
                ) = get_rent_data(region)

                professions_by_sector = helpers.get_sector_professions_by_level(triage_data.sector)

                home_url = '/international/expand-your-business-in-the-uk/guide/'
                if request.GET.get('back'):
                    home_url += '#tailored-guide'

                breadcrumbs = [
                    {'name': 'Home', 'url': '/international/'},
                    {
                        'name': 'Your expansion guide',
                        'url': '/international/expand-your-business-in-the-uk/guide/#tailored-guide',
                    },
                ]

                context.update(
                    triage_data=triage_data,
                    location_form=LocationSelectForm(initial={'location': location}),
                    entry_salary=cleaned_median_salaries.get(professions.ENTRY_LEVEL),
                    mid_salary=cleaned_median_salaries.get(professions.MID_SENIOR_LEVEL),
                    executive_salary=cleaned_median_salaries.get(professions.DIRECTOR_EXECUTIVE_LEVEL),
                    salary_error_msg=cleaned_median_salaries.get('error_msg'),
                    large_warehouse_rent=large_warehouse_rent,
                    small_warehouse_rent=small_warehouse_rent,
                    shopping_centre=shopping_centre,
                    high_street_retail=high_street_retail,
                    work_office=work_office,
                    professions_by_sector=professions_by_sector,
                    show_salary_component=show_salary_component,
                    show_rent_component=show_rent_component,
                    breadcrumbs=breadcrumbs,
                )

        site_section_url = ''
        if self.url:
            site_section_url = str(self.url or '/').split('/')[4]
        self.set_ga360_payload(
            page_id='Article',
            business_unit='ExpandYourBusiness',
            site_section=site_section_url,
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        self.set_csat_and_stage(request, context, self.hcsat_service_name, self.get_csat_form)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        self.set_is_csat_complete(request, context)

        return context


class EYBTradeShowsPage(WagtailCacheMixin, BaseContentPage, EYBHCSAT):
    parent_page_types = ['international_online_offer.EYBGuidePage']
    subpage_types = ['international_online_offer.IOOTradeShowPage']
    template = 'eyb/trade_shows.html'

    def serve(self, request, *args, **kwargs):
        # hcsat
        if request.method == 'POST':
            return self.post(request)
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        triage_data = get_triage_data_for_user(request)
        all_tradeshows = []

        if triage_data and triage_data.sector:
            """
            Wagtail doesn't allow commas in tags and we need to match the sector
            'Agriculture, horticulture, fisheries and pets' i.e. below will match the tag
            'Agriculture horticulture fisheries and pets'
            """
            user_sector = triage_data.sector.replace(',', '')
            all_tradeshows = IOOTradeShowPage.objects.live().filter(tags__name__iexact=user_sector)

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {
                'name': 'Your expansion guide',
                'url': '/international/expand-your-business-in-the-uk/guide/#tailored-guide',
            },
        ]
        context.update(
            triage_data=triage_data,
            all_tradeshows=all_tradeshows,
            breadcrumbs=breadcrumbs,
        )
        self.set_ga360_payload(
            page_id='TradeShows',
            business_unit='ExpandYourBusiness',
            site_section='trade-shows',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        self.set_csat_and_stage(request, context, self.hcsat_service_name, self.get_csat_form)
        if 'form' in kwargs:  # pass back errors from form_invalid
            context['hcsat_form'] = kwargs['form']

        self.set_is_csat_complete(request, context)

        return context


class EYBTradeShowPageTag(TaggedItemBase):
    tag = models.ForeignKey(EYBArticleTag, related_name='eyb_tagged_tradeshows', on_delete=models.CASCADE)
    content_object = ParentalKey(
        'international_online_offer.IOOTradeShowPage', related_name='eyb_tradeshow_tagged_items'
    )


class IOOTradeShowPage(BaseContentPage):
    parent_page_types = ['international_online_offer.EYBTradeShowsPage']
    subpage_types = []
    template = 'eyb/trade_shows.html'
    tradeshow_title = models.TextField()
    tradeshow_subheading = StreamField(
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
    tradeshow_link = models.URLField(blank=True, max_length=255, null=True)
    tags = ClusterTaggableManager(
        through=EYBTradeShowPageTag,
        blank=True,
        verbose_name='Trade Show Tags',
        help_text="A comma-separated list of tags. Do not include commas in the sector name, e.g. 'Agriculture, horticulture, fisheries and pets' is tagged as 'Agriculture horticulture fisheries and pets'",  # noqa:E501
    )
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('tradeshow_title'),
        FieldPanel('tradeshow_subheading'),
        FieldPanel('tradeshow_link'),
        FieldPanel('tags'),
    ]


class EYBArticlesPage(BaseContentPage):
    parent_page_types = ['international_online_offer.EYBGuidePage', 'international_online_offer.EYBArticlesPage']
    subpage_types = ['international_online_offer.EYBArticlePage', 'international_online_offer.EYBArticlesPage']


class TriageData(TimeStampedModel):
    hashed_uuid = models.CharField(max_length=200)
    sector = models.CharField(max_length=255)
    sector_sub = models.CharField(max_length=255, default=None, null=True)
    sector_sub_sub = models.CharField(max_length=255, default=None, null=True)
    sector_id = models.CharField(default=None, null=True)
    intent = ArrayField(
        models.CharField(max_length=255, choices=choices.INTENT_CHOICES),
        size=6,
        default=list,
    )

    def get_intent_display(self):
        out = []
        for display_intent in choices.INTENT_CHOICES:
            if self.intent and display_intent[0] in self.intent:
                out.append(display_intent[1])
        return out

    intent_other = models.CharField(max_length=255)
    location = models.CharField(max_length=255, choices=choices.REGION_CHOICES)
    location_city = models.CharField(
        max_length=255, default=None, null=True, choices=region_sector_helpers.generate_location_choices(False)
    )
    location_none = models.BooleanField(default=None, null=True)
    hiring = models.CharField(max_length=255, choices=choices.HIRING_CHOICES)
    spend = models.CharField(max_length=255, choices=choices.SPEND_CHOICES)
    spend_other = models.CharField(max_length=255, null=True)
    is_high_value = models.BooleanField(default=False)


class UserData(TimeStampedModel):
    hashed_uuid = models.CharField(max_length=200)
    company_name = models.CharField(max_length=255)
    company_location = models.CharField(max_length=255)
    duns_number = models.CharField(max_length=255, null=True, blank=True)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    county = models.CharField(max_length=255, null=True, blank=True)
    postcode = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    telephone_number = models.CharField(max_length=255)
    agree_terms = models.BooleanField(default=False)
    agree_info_email = models.BooleanField(default=False)
    landing_timeframe = models.CharField(
        null=True, default=None, max_length=255, choices=choices.LANDING_TIMEFRAME_CHOICES
    )
    company_website = models.CharField(max_length=255, null=True)


class TradeAssociation(models.Model):
    trade_association_id = models.CharField(max_length=255)
    sector_grouping = models.CharField(max_length=255)
    association_name = models.CharField(max_length=255)
    website_link = models.CharField(max_length=255)
    sector = models.CharField(max_length=255)
    brief_description = models.CharField(max_length=255)
    link_valid = models.BooleanField(default=True, null=True)


class SalaryData(models.Model):
    region = models.CharField(max_length=255)
    vertical = models.CharField(max_length=255)
    professional_level = models.CharField(max_length=255)
    median_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mean_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class RentData(models.Model):
    region = models.CharField(max_length=255)
    sub_vertical = models.CharField(max_length=255)
    gbp_per_square_foot_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    square_feet = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    gbp_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)
