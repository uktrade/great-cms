from itertools import chain

from django import forms
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Avg
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey
from taggit.models import TagBase, TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.field_block import RichTextBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

from core.blocks import ColumnsBlock
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
from international_online_offer.forms import LocationSelectForm
from international_online_offer.services import get_median_salaries, get_rent_data


class EYBIndexPage(BaseContentPage):
    parent_page_types = [
        'domestic.StructuralPage',
        'international.GreatInternationalHomePage',
    ]
    subpage_types = [
        'international_online_offer.EYBGuidePage',
    ]
    template = 'eyb/index.html'

    # TODO remove after general election AND sign up to front branch merged
    if settings.FEATURE_PRE_ELECTION and settings.FEATURE_EYB_HOME:
        template = 'eyb/index-new.html'


def get_triage_data_for_user(request):
    if hasattr(request, 'user') and hasattr(request, 'session'):
        if hasattr(request.user, 'is_authenticated'):
            if not request.user.is_authenticated:
                return TriageData(
                    sector=request.session.get('sector'),
                    intent=request.session.get('intent'),
                    intent_other=request.session.get('intent_other'),
                    location=request.session.get('location'),
                    location_none=request.session.get('location_none'),
                    hiring=request.session.get('hiring'),
                    spend=request.session.get('spend'),
                    spend_other=request.session.get('spend_other'),
                    is_high_value=request.session.get('is_high_value'),
                )
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


class EYBGuidePage(BaseContentPage):
    parent_page_types = ['international_online_offer.EYBIndexPage']
    subpage_types = [
        'international_online_offer.EYBArticlePage',
        'international_online_offer.EYBTradeShowsPage',
        'international_online_offer.EYBArticlesPage',
    ]
    template = 'eyb/guide.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        user_data = get_user_data_for_user(request)
        triage_data = get_triage_data_for_user(request)
        is_triage_complete = helpers.is_triage_complete(triage_data)

        bci_data = None
        if triage_data and triage_data.sector:
            bci_data = services.get_bci_data_by_dbt_sector(triage_data.sector.replace('_', ' '), [regions.GB_GEO_CODE])

        # Get trade shows page (should only be one, is a parent / container page for all trade show pages)
        trade_shows_page = EYBTradeShowsPage.objects.live().filter().first()

        # Get any EYB articles that have been tagged with user selected sector
        all_articles_tagged_with_sector = (
            EYBArticlePage.objects.live().filter(tags__name=triage_data.sector)
            if triage_data and triage_data.sector
            else []
        )
        # Get any EYB articles that have been tagged with user selected intent(s)
        all_articles_tagged_with_intent = (
            EYBArticlePage.objects.live().filter(tags__name__in=triage_data.intent)
            if triage_data and triage_data.intent
            else []
        )
        # Get any EYB articles that have been tagged with FINANCE_AND_SUPPORT
        all_articles_tagged_with_finance_and_support = EYBArticlePage.objects.live().filter(
            tags__name=filter_tags.FINANCE_AND_SUPPORT
        )

        # Filter rule to get articles that have ONLY been tagged with the users selected sector
        sector_only_articles = helpers.filter_articles_sector_only(all_articles_tagged_with_sector)
        # Filter rule to get intent articles that are tagged with the users selected sector
        intent_articles_specific_to_sector = (
            helpers.filter_intent_articles_specific_to_sector(all_articles_tagged_with_intent, triage_data.sector)
            if triage_data and triage_data.sector
            else []
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
            get_to_know_market_articles=list(chain(sector_only_articles, intent_articles_specific_to_sector)),
            finance_and_support_articles=all_articles_tagged_with_finance_and_support,
            trade_shows_page=trade_shows_page,
            is_triage_complete=is_triage_complete,
            breadcrumbs=breadcrumbs,
        )

        self.set_ga360_payload(
            page_id='Guide',
            business_unit='ExpandYourBusiness',
            site_section='guide',
        )
        self.add_ga360_data_to_payload(request)
        context['ga360'] = self.ga360_payload

        return context


class EYBArticleTag(TagBase):
    """EYB article tag for filtering out content based on triage answers."""

    class Meta:
        verbose_name = 'EYB article tag for link to triage answer'
        verbose_name_plural = 'EYB article tags for links to triage answers'


class EYBArticlePageTag(TaggedItemBase):
    tag = models.ForeignKey(EYBArticleTag, related_name='ioo_tagged_articles', on_delete=models.CASCADE)
    content_object = ParentalKey('international_online_offer.EYBArticlePage', related_name='ioo_article_tagged_items')


class EYBArticlePage(BaseContentPage):
    parent_page_types = [
        'international_online_offer.EYBGuidePage',
        'international_online_offer.EYBArticlesPage',
    ]
    subpage_types = []
    template = 'eyb/article.html'
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
    tags = ClusterTaggableManager(through=EYBArticlePageTag, blank=True, verbose_name='Article Tags')
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        FieldPanel('article_image'),
        FieldPanel('article_body'),
        FieldPanel('tags'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if helpers.is_authenticated(request):
            triage_data = get_triage_data_for_user(request)

            tags = self.tags.all()
            show_salary_component = helpers.can_show_salary_component(tags)
            show_rent_component = helpers.can_show_rent_component(tags)

            if triage_data and settings.FEATURE_PRE_ELECTION:
                # This if statement contains some duplicated code from below elif. This is to ensure that when
                # we are releasing to production post-election we can simply remove the elif code.

                location = request.GET.get(
                    'location', triage_data.location if triage_data.location else choices.regions.LONDON
                )
                region = helpers.get_salary_region_from_region(location)
                sector_display = triage_data.get_sector_display()

                median_salaries = get_median_salaries(sector_display, geo_region=region)
                cleaned_median_salaries = helpers.clean_salary_data(median_salaries)

                (large_warehouse_rent, small_warehouse_rent, shopping_centre, high_street_retail, work_office) = (
                    get_rent_data(region)
                )

                professions_by_sector = helpers.get_sector_professions_by_level(triage_data.sector)

                home_url = '/international/expand-your-business-in-the-uk/guide/'
                if request.GET.get('back'):
                    home_url += '#personalised-guide'

                breadcrumbs = [
                    {'name': 'Home', 'url': '/international/'},
                    {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
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

            elif triage_data:
                location = request.GET.get(
                    'location', triage_data.location if triage_data.location else choices.regions.LONDON
                )
                region = helpers.get_salary_region_from_region(location)
                sector_display = triage_data.get_sector_display()

                entry_salary = SalaryData.objects.filter(
                    region__iexact=region,
                    vertical__icontains=sector_display,
                    professional_level__icontains='Entry-level',
                ).aggregate(Avg('median_salary'))
                mid_salary = SalaryData.objects.filter(
                    region__iexact=region,
                    vertical__icontains=sector_display,
                    professional_level__icontains='Middle/Senior Management',
                ).aggregate(Avg('median_salary'))
                executive_salary = SalaryData.objects.filter(
                    region__iexact=region,
                    vertical__icontains=sector_display,
                    professional_level__icontains='Director/Executive',
                ).aggregate(Avg('median_salary'))

                entry_salary, mid_salary, executive_salary = helpers.get_salary_data(
                    entry_salary, mid_salary, executive_salary
                )

                large_warehouse_rent = RentData.objects.filter(
                    region__iexact=region, sub_vertical='Large Warehouses'
                ).first()
                small_warehouse_rent = RentData.objects.filter(
                    region__iexact=region, sub_vertical='Small Warehouses'
                ).first()
                shopping_centre = RentData.objects.filter(
                    region__iexact=region, sub_vertical='Prime shopping centre'
                ).first()
                high_street_retail = RentData.objects.filter(
                    region__iexact=region, sub_vertical='High Street Retail'
                ).first()
                work_office = RentData.objects.filter(region__iexact=region, sub_vertical='Work Office').first()

                (
                    large_warehouse_rent,
                    small_warehouse_rent,
                    shopping_centre,
                    high_street_retail,
                    work_office,
                ) = helpers.get_rent_data(
                    large_warehouse_rent, small_warehouse_rent, shopping_centre, high_street_retail, work_office
                )

                professions_by_sector = helpers.get_sector_professions_by_level(triage_data.sector)

                home_url = '/international/expand-your-business-in-the-uk/guide/'
                if request.GET.get('back'):
                    home_url += '#personalised-guide'

                breadcrumbs = [
                    {'name': 'Home', 'url': '/international/'},
                    {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
                ]

                context.update(
                    triage_data=triage_data,
                    location_form=LocationSelectForm(initial={'location': location}),
                    entry_salary=entry_salary,
                    mid_salary=mid_salary,
                    executive_salary=executive_salary,
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
        return context


class EYBTradeShowsPage(BaseContentPage):
    parent_page_types = ['international_online_offer.EYBGuidePage']
    subpage_types = ['international_online_offer.IOOTradeShowPage']
    template = 'eyb/trade_shows.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        triage_data = get_triage_data_for_user(request)
        all_tradeshows = []

        if triage_data:
            all_tradeshows = (
                IOOTradeShowPage.objects.live().filter(tags__name=triage_data.sector) if triage_data.sector else []
            )

        breadcrumbs = [
            {'name': 'Home', 'url': '/international/'},
            {'name': 'Guide', 'url': '/international/expand-your-business-in-the-uk/guide/#personalised-guide'},
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
        return context


class EYBTradeShowPageTag(TaggedItemBase):
    tag = models.ForeignKey(EYBArticleTag, related_name='eyb_tagged_tradeshows', on_delete=models.CASCADE)
    content_object = ParentalKey(
        'international_online_offer.IOOTradeShowPage', related_name='eyb_tradeshow_tagged_items'
    )


class IOOTradeShowPage(BaseContentPage):
    parent_page_types = ['international_online_offer.EYBTradeShowsPage']
    subpage_types = []
    template = 'eyb/trade-shows.html'
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
    tags = ClusterTaggableManager(through=EYBTradeShowPageTag, blank=True, verbose_name='Trade Show Tags')
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
    sector = models.CharField(max_length=255, choices=region_sector_helpers.generate_sector_choices())
    sector_sub = models.CharField(
        max_length=255, choices=region_sector_helpers.generate_sector_sic_choices(), default=None, null=True
    )
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
    location_none = models.BooleanField(default=False)
    hiring = models.CharField(max_length=255, choices=choices.HIRING_CHOICES)
    spend = models.CharField(max_length=255, choices=choices.SPEND_CHOICES)
    spend_other = models.CharField(max_length=255, null=True)
    is_high_value = models.BooleanField(default=False)


class UserData(TimeStampedModel):
    hashed_uuid = models.CharField(max_length=200)
    company_name = models.CharField(max_length=255)
    company_location = models.CharField(max_length=255, choices=choices.COMPANY_LOCATION_CHOICES)
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


class CsatFeedback(TimeStampedModel):
    URL = models.CharField(max_length=255)
    user_journey = models.CharField(max_length=255, null=True)
    satisfaction_rating = models.CharField(max_length=255, choices=choices.SATISFACTION_CHOICES)
    experienced_issue = ArrayField(
        models.CharField(max_length=255, choices=choices.EXPERIENCE_CHOICES), size=6, default=list, null=True
    )
    other_detail = models.CharField(max_length=255, null=True)
    service_improvements_feedback = models.CharField(max_length=255, null=True)
    likelihood_of_return = models.CharField(max_length=255, choices=choices.LIKELIHOOD_CHOICES, null=True)
    site_intentions = ArrayField(
        models.CharField(max_length=255, choices=choices.INTENSION_CHOICES), size=6, default=list, null=True
    )
    site_intentions_other = models.CharField(max_length=255, null=True)


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


class ScorecardCriterion(models.Model):
    sector = models.CharField(max_length=255)
    capex_spend = models.IntegerField(null=True, blank=True)
    labour_workforce_hire = models.IntegerField(null=True, blank=True)
    high_potential_opportunity_locations = ChoiceArrayField(
        base_field=models.CharField(max_length=255, choices=choices.REGION_CHOICES), default=list, null=True, blank=True
    )
