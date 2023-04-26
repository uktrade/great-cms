from django.contrib.postgres.fields import ArrayField
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey
from taggit.models import TagBase, TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks.field_block import RichTextBlock
from wagtail.core.blocks.stream_block import StreamBlock
from wagtail.core.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from core.blocks import ColumnsBlock
from core.models import CMSGenericPage
from directory_constants.choices import COUNTRY_CHOICES
from domestic.models import BaseContentPage
from international_online_offer.core import choices, helpers


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
    if hasattr(request, 'user') and request.user.is_authenticated:
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
    if hasattr(request, 'user') and request.user.is_authenticated:
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
    LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = (
        'Complete the contact form to keep up to date with our personalised service.'
    )
    HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE = """Your business qualifies for 1 to 1 support from specialist UK
        government advisors. Complete the form to access this and keep up to date with our
        personalised service."""
    parent_page_types = ['international_online_offer.IOOIndexPage']
    subpage_types = ['international_online_offer.IOOArticlePage']
    template = 'ioo/guide.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        triage_data = get_triage_data_from_db_or_session(request)
        user_data = get_user_data_from_db_or_session(request)
        all_articles = self.get_children().live()
        get_to_know_market_articles = []
        opportunities_articles = []
        complete_contact_form_message = self.LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
        if triage_data:
            if triage_data.is_high_value:
                complete_contact_form_message = self.HIGH_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
            get_to_know_market_articles = helpers.find_get_to_know_market_articles(
                all_articles, triage_data.sector, triage_data.intent
            )
            opportunities_articles = helpers.find_opportunities_articles(all_articles, triage_data.sector)
        support_and_incentives_articles = helpers.find_get_support_and_incentives_articles(all_articles)
        context.update(
            complete_contact_form_message=complete_contact_form_message,
            complete_contact_form_link='international_online_offer:signup',
            complete_contact_form_link_text='Complete form',
            triage_data=triage_data,
            user_data=user_data,
            get_to_know_market_articles=get_to_know_market_articles,
            support_and_incentives_articles=support_and_incentives_articles,
            opportunities_articles=opportunities_articles,
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
        null=True,
        blank=True,
    )
    tags = ClusterTaggableManager(through=IOOArticlePageTag, blank=True, verbose_name='Article Tags')
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        StreamFieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        ImageChooserPanel('article_image'),
        StreamFieldPanel('article_body'),
        FieldPanel('tags'),
    ]


class TriageData(models.Model):
    hashed_uuid = models.CharField(max_length=200)
    sector = models.CharField(max_length=255, choices=choices.SECTOR_CHOICES)
    intent = ArrayField(
        ArrayField(
            models.CharField(max_length=255, choices=choices.INTENT_CHOICES),
            size=6,
        ),
        size=1,
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
