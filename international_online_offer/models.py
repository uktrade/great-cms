from django.contrib.postgres.fields import ArrayField
from django.core.paginator import Paginator
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
from core.models import CMSGenericPage
from directory_constants.choices import COUNTRY_CHOICES
from domestic.models import BaseContentPage
from international_online_offer.core import choices, constants, helpers
from international_online_offer.forms import LocationSelectForm


def get_triage_data(hashed_uuid):
    try:
        return TriageData.objects.get(hashed_uuid=hashed_uuid)
    except TriageData.DoesNotExist:
        return None


def get_user_data(hashed_uuid):
    try:
        return UserData.objects.get(hashed_uuid=hashed_uuid)
    except UserData.DoesNotExist:
        return None


def get_triage_data_from_db_or_session(request):
    if hasattr(request, 'user'):
        if hasattr(request.user, 'is_authenticated'):
            if request.user.is_authenticated:
                if hasattr(request.user, 'hashed_uuid'):
                    triage_data = get_triage_data(request.user.hashed_uuid)
                    if triage_data:
                        return triage_data
    if hasattr(request, 'session'):
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


def get_user_data_from_db_or_session(request):
    if hasattr(request, 'user'):
        if hasattr(request.user, 'is_authenticated'):
            if request.user.is_authenticated:
                if hasattr(request.user, 'hashed_uuid'):
                    user_data = get_user_data(request.user.hashed_uuid)
                    if user_data:
                        return user_data

    if hasattr(request, 'session'):
        return UserData(
            company_name=request.session.get('company_name'),
            company_location=request.session.get('company_location'),
            full_name=request.session.get('full_name'),
            role=request.session.get('role'),
            email=request.session.get('email'),
            telephone_number=request.session.get('telephone_number'),
            agree_terms=request.session.get('agree_terms'),
            agree_info_email=request.session.get('agree_info_email'),
            agree_info_telephone=request.session.get('agree_info_telephone'),
        )


class IOOIndexPage(BaseContentPage):
    parent_page_types = [
        'domestic.StructuralPage',
    ]
    subpage_types = [
        'international_online_offer.IOOGuidePage',
    ]
    template = 'ioo/index.html'


class IOOGuidePage(BaseContentPage):
    parent_page_types = ['international_online_offer.IOOIndexPage']
    subpage_types = ['international_online_offer.IOOArticlePage', 'international_online_offer.IOOTradePage']
    template = 'ioo/guide.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        triage_data = get_triage_data_from_db_or_session(request)
        user_data = get_user_data_from_db_or_session(request)
        trade_page = helpers.get_trade_page(self.get_children().live().type(IOOTradePage))
        all_articles = self.get_children().live().type(IOOArticlePage)
        get_to_know_market_articles = []
        opportunities_articles = []
        complete_contact_form_message = constants.LOW_VALUE_INVESTOR_SIGNUP_MESSAGE
        if triage_data:
            if triage_data.is_high_value:
                complete_contact_form_message = constants.HIGH_VALUE_INVESTOR_SIGNUP_MESSAGE
            get_to_know_market_articles = helpers.find_get_to_know_market_articles(
                all_articles, triage_data.sector, triage_data.intent
            )
            opportunities_articles = helpers.find_opportunities_articles(all_articles, triage_data.sector)
        support_and_incentives_articles = helpers.find_get_support_and_incentives_articles(all_articles)
        context.update(
            complete_contact_form_message=complete_contact_form_message,
            complete_contact_form_link='international_online_offer:signup',
            complete_contact_form_link_text='Sign up',
            triage_data=triage_data,
            user_data=user_data,
            get_to_know_market_articles=get_to_know_market_articles,
            support_and_incentives_articles=support_and_incentives_articles,
            opportunities_articles=opportunities_articles,
            trade_page=trade_page,
        )
        return context


class IOOArticleTag(TagBase):
    """IOO article tag for filtering out content based on triage answers."""

    class Meta:
        verbose_name = 'IOO article tag for link to triage answer'
        verbose_name_plural = 'IOO article tags for links to triage answers'


class IOOArticlePageTag(TaggedItemBase):
    tag = models.ForeignKey(IOOArticleTag, related_name='ioo_tagged_articles', on_delete=models.CASCADE)
    content_object = ParentalKey('international_online_offer.IOOArticlePage', related_name='ioo_article_tagged_items')


class IOOArticlePage(BaseContentPage):
    parent_page_types = [
        'international_online_offer.IOOGuidePage',
    ]
    subpage_types = []
    template = 'ioo/article.html'
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
    tags = ClusterTaggableManager(through=IOOArticlePageTag, blank=True, verbose_name='Article Tags')
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
        if helpers.is_expand_your_business_registered(request):
            triage_data = get_triage_data(request.user.hashed_uuid)
            location = request.GET.get('location', triage_data.location)
            region = helpers.get_salary_region_from_region(location)
            sector_display = triage_data.get_sector_display()

            entry_salary = SalaryData.objects.filter(
                region=region, vertical__iexact=sector_display, professional_level='Entry-level'
            ).aggregate(Avg('median_salary'))
            mid_salary = SalaryData.objects.filter(
                region=region, vertical__iexact=sector_display, professional_level='Middle/Senior Management'
            ).aggregate(Avg('median_salary'))
            executive_salary = SalaryData.objects.filter(
                region=region, vertical__iexact=sector_display, professional_level='Director/Executive'
            ).aggregate(Avg('median_salary'))

            entry_salary = entry_salary.get('median_salary__avg')
            mid_salary = mid_salary.get('median_salary__avg')
            executive_salary = executive_salary.get('median_salary__avg')

            if entry_salary:
                entry_salary = int(entry_salary)
            if mid_salary:
                mid_salary = int(mid_salary)
            if executive_salary:
                executive_salary = int(executive_salary)

        context.update(
            triage_data=triage_data,
            location_form=LocationSelectForm(initial={'location': location}),
            entry_salary=entry_salary,
            mid_salary=mid_salary,
            executive_salary=executive_salary,
        )
        return context


class IOOTradePage(BaseContentPage):
    parent_page_types = ['international_online_offer.IOOGuidePage']
    subpage_types = ['international_online_offer.IOOTradeShowPage']
    template = 'ioo/trade.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        triage_data = get_triage_data_from_db_or_session(request)
        all_tradeshows = []
        all_trade_associations = []
        if triage_data:
            all_tradeshows = helpers.find_trade_shows_for_sector(
                self.get_children().live().type(IOOTradeShowPage), triage_data.sector
            )
            # Given the sector selected we need to get mapped trade association sectors to query
            # with due to misalignment of sector names across DBT
            trade_association_sectors = helpers.get_trade_assoication_sectors_from_sector(triage_data.sector)
            all_trade_associations = TradeAssociation.objects.filter(sector__in=trade_association_sectors)
            # if we still have no matching trade associations then we'll
            # try a search based a sector display name that we might not have mapped yet
            if len(all_trade_associations) == 0:
                all_trade_associations = TradeAssociation.objects.filter(sector=triage_data.get_sector_display())

        page = request.GET.get('page', 1)
        paginator = Paginator(all_trade_associations, 10)
        all_trade_associations = paginator.page(page)
        context.update(
            triage_data=triage_data, all_tradeshows=all_tradeshows, all_trade_associations=all_trade_associations
        )
        return context


class IOOTradeShowPageTag(TaggedItemBase):
    tag = models.ForeignKey(IOOArticleTag, related_name='ioo_tagged_tradeshows', on_delete=models.CASCADE)
    content_object = ParentalKey(
        'international_online_offer.IOOTradeShowPage', related_name='ioo_tradeshow_tagged_items'
    )


class IOOTradeShowPage(BaseContentPage):
    parent_page_types = ['international_online_offer.IOOTradePage']
    subpage_types = []
    template = 'ioo/trade.html'
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
    tags = ClusterTaggableManager(through=IOOTradeShowPageTag, blank=True, verbose_name='Trade Show Tags')
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('tradeshow_title'),
        FieldPanel('tradeshow_subheading'),
        FieldPanel('tradeshow_link'),
        FieldPanel('tags'),
    ]


class TriageData(models.Model):
    hashed_uuid = models.CharField(max_length=200)
    sector = models.CharField(max_length=255, choices=choices.SECTOR_CHOICES)
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
    location_none = models.BooleanField(default=False)
    hiring = models.CharField(max_length=255, choices=choices.HIRING_CHOICES)
    spend = models.CharField(max_length=255, choices=choices.SPEND_CHOICES)
    spend_other = models.CharField(max_length=255, null=True)
    is_high_value = models.BooleanField(default=False)


class UserData(models.Model):
    hashed_uuid = models.CharField(max_length=200)
    company_name = models.CharField(max_length=255)
    company_location = models.CharField(max_length=255, choices=COUNTRY_CHOICES)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    telephone_number = models.CharField(max_length=255)
    agree_terms = models.BooleanField(default=False)
    agree_info_email = models.BooleanField(default=False)
    agree_info_telephone = models.BooleanField(default=False)


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
    occupation = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True)
    year = models.IntegerField(null=True)
    number_of_jobs_thousands = models.IntegerField(null=True)
    median_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    median_annual_percentage_change = models.IntegerField(null=True)
    mean_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mean_annual_percentage_change = models.IntegerField(null=True)
