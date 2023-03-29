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
from domestic.models import BaseContentPage


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
    CONTACT_FORM_SUCCESS_MESSAGE = 'Thank you for completing the contact form.'
    parent_page_types = ['international_online_offer.IOOIndexPage']
    subpage_types = ['international_online_offer.IOOArticlePage']
    template = 'ioo/guide.html'

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            complete_contact_form_message=self.LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE,
            complete_contact_form_link='international_online_offer:contact',
            complete_contact_form_link_text='Complete form',
            contact_form_success_message=self.CONTACT_FORM_SUCCESS_MESSAGE,
            submit_contact_details_success=request.GET.get('success'),
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
    article_subheading = models.TextField(
        blank=True,
        help_text='This is a subheading that displays below the main title on the article page',
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
                    min_num=3,
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
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        ImageChooserPanel('article_image'),
        StreamFieldPanel('article_body'),
        FieldPanel('tags'),
    ]


class TriageData(models.Model):
    hashed_uuid = models.CharField(max_length=200)

    SECTOR_CHOICES = (
        ('Advanced engineering', 'Advanced engineering'),
        ('Aerospace', 'Aerospace'),
        ('Agriculture, Horticulture, Fisheries and pets', 'Agriculture, Horticulture, Fisheries and pets'),
        ('Airports', 'Airports'),
        ('Automotive', 'Automotive'),
        ('Biotech and Pharmaceuticals', 'Biotech and Pharmaceuticals'),
        ('Business and consumer services', 'Business and consumer services'),
        ('Chemicals', 'Chemicals'),
        ('Construction', 'Construction'),
        ('Consumer and retail', 'Consumer and retail'),
        ('Creative industries', 'Creative industries'),
        ('Defense and Security', 'Defense and Security'),
        ('Education and Training', 'Education and Training'),
        ('Energy', 'Energy'),
        ('Environment', 'Environment'),
        ('Financial and Professional Services', 'Financial and Professional Services'),
        ('Food and Drink', 'Food and Drink'),
        ('Healthcare and Medical', 'Healthcare and Medical'),
        ('Infrastructure Air and Sea', 'Infrastructure Air and Sea'),
        ('Leisure', 'Leisure'),
        ('Logistics', 'Logistics'),
        ('Manufacturing', 'Manufacturing'),
        ('Marine', 'Marine'),
        ('Maritime Services', 'Maritime Services'),
        ('Medical devices and equipment', 'Medical devices and equipment'),
        ('Mining', 'Mining'),
        ('Nuclear', 'Nuclear'),
        ('Oil and Gas', 'Oil and Gas'),
        ('Rail', 'Rail'),
        ('Renewable', 'Renewable'),
        ('Retail', 'Retail'),
        ('Security', 'Security'),
        ('Space', 'Space'),
        ('Sports Events', 'Sports Events'),
        ('Technology and Smart Cities', 'Technology and Smart Cities'),
    )

    sector = models.CharField(max_length=255, choices=SECTOR_CHOICES)

    INTENT_CHOICES = (
        ('Set up new premises', 'Set up new premises'),
        ('Set up a new distribution centre', 'Set up a new distribution centre'),
        ('Onward sales and exports from the UK', 'Onward sales and exports from the UK'),
        ('Research, develop and collaborate', 'Research, develop and collaborate'),
        ('Find people with specialist skills', 'Find people with specialist skills'),
        ('Other', 'Other'),
    )

    intent = ArrayField(
        ArrayField(
            models.CharField(max_length=255, choices=INTENT_CHOICES),
            size=6,
        ),
        size=1,
        default=list,
    )
    intent_other = models.CharField(max_length=255)

    LOCATION_CHOICES = (
        ('East', 'East'),
        ('East Midlands', 'East Midlands'),
        ('London', 'London'),
        ('North East', 'North East'),
        ('North West', 'North West'),
        ('Northern Ireland', 'Northern Ireland'),
        ('Scotland', 'Scotland'),
        ('South East', 'South East'),
        ('South West', 'South West'),
        ('Wales', 'Wales'),
        ('West Midlands', 'West Midlands'),
        ('Yorkshire and the Humber', 'Yorkshire and the Humber'),
    )

    location = models.CharField(max_length=255, choices=LOCATION_CHOICES)
    location_none = models.BooleanField(default=False)

    HIRING_CHOICES = (
        ('1-10', '1 to 10'),
        ('11-50', '11 to 50'),
        ('51-100', '51 to 100'),
        ('101+', 'More than 100'),
        ('No plans to hire yet', 'No plans to hire yet'),
    )

    hiring = models.CharField(max_length=255, choices=HIRING_CHOICES)

    SPEND_CHOICES = (
        ('10000-500000', '£10,000 - £500,000'),
        ('500001-1000000', '£500,000 - £1,000,000'),
        ('1000001-2000000', '£1,000,001 - £2,000,000'),
        ('2000001-5000000', '£2,000,001 - £5,000,000'),
        ('5000001-10000000', '£5,000,001 - £10,000,000'),
        ('10000000+', 'More than £10 million'),
        ('Specific amount', 'Specific amount'),
    )

    spend = models.CharField(max_length=255, choices=SPEND_CHOICES)
    spend_other = models.CharField(max_length=255, null=True)


class UserData(models.Model):
    hashed_uuid = models.CharField(max_length=200)
    company_name = models.CharField(max_length=255)
    LOCATION_CHOICES = (
        ('France', 'France'),
        ('Germany', 'Germany'),
        ('India', 'India'),
        ('Italy', 'Italy'),
        ('Spain', 'Spain'),
        ('United States', 'United States'),
    )
    company_location = models.CharField(max_length=255, choices=LOCATION_CHOICES)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    telephone_number = models.CharField(max_length=255)
    agree_terms = models.BooleanField(default=False)
    agree_info_email = models.BooleanField(default=False)
    agree_info_telephone = models.BooleanField(default=False)
