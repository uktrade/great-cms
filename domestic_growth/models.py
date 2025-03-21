from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.blocks.stream_block import StreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet
from wagtailseo.models import SeoMixin

from core.models import TimeStampedModel
from domestic_growth import cms_panels, helpers
from domestic_growth.blocks import DomesticGrowthCardBlock
from international_online_offer.models import TradeAssociation


class DomesticGrowthHomePage(SeoMixin, cms_panels.DomesticGrowthHomePagePanels, Page):
    template = 'home.html'

    class Meta:
        verbose_name = 'Domestic Growth Home page'

    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    hero_title = models.TextField(
        null=True,
    )

    hero_intro = models.TextField(
        null=True,
    )

    explore_title = models.TextField(
        null=True,
        blank=True,
    )

    explore_body = StreamField(
        [
            (
                'explore_cards',
                StreamBlock(
                    [
                        ('explore_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'explore_card': {'min_num': 4},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    guidance_title = models.TextField(
        null=True,
    )

    guidance_body = StreamField(
        [
            (
                'guidance_cards',
                StreamBlock(
                    [
                        ('guidance_card', DomesticGrowthCardBlock()),
                    ],
                    block_counts={
                        'guidance_card': {'min_num': 4},
                    },
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
    )

    about_title = models.TextField(
        null=True,
    )

    about_intro = models.TextField(
        null=True,
    )

    about_description = models.TextField(
        null=True,
    )

    news_title = models.TextField(
        null=True,
    )

    news_link_text = models.TextField(
        null=True,
    )

    news_link_url = models.TextField(
        null=True,
    )

    feedback_title = models.TextField(
        null=True,
    )

    feedback_description = models.TextField(
        null=True,
    )

    feedback_link_text = models.TextField(
        null=True,
    )

    feedback_link_url = models.TextField(
        null=True,
    )

    def get_context(self, request):
        context = super(DomesticGrowthHomePage, self).get_context(request)
        context['news'] = helpers.get_dbt_news_articles()
        context['trade_associations'] = TradeAssociation.objects.all()
        return context


class DomesticGrowthGuidePage(SeoMixin, cms_panels.DomesticGrowthGuidePagePanels, Page):
    template = 'guide.html'

    class Meta:
        verbose_name = 'Domestic Growth Guide page'

    subpage_types = ['domestic_growth.DomesticGrowthChildGuidePage']

    hero_title = models.TextField(
        null=True,
    )

    hero_intro = models.TextField(
        null=True,
    )

    body_title = models.TextField(
        null=True,
    )

    body_intro = models.TextField(
        null=True,
    )


class DomesticGrowthChildGuidePage(SeoMixin, cms_panels.DomesticGrowthChildGuidePagePanels, Page):
    template = 'guide-child.html'

    class Meta:
        verbose_name = 'Domestic Growth Child Guide page'

    parent_page_types = [
        'domestic_growth.DomesticGrowthGuidePage',
    ]

    body_title = models.TextField(
        null=True,
    )

    body_intro = models.TextField(
        null=True,
    )

    body_sections = StreamField(
        [
            (
                'section',
                blocks.StructBlock(
                    [
                        ('title', blocks.CharBlock()),
                        ('intro', blocks.CharBlock()),
                        (
                            'content',
                            blocks.ListBlock(
                                SnippetChooserBlock('domestic_growth.DomesticGrowthContent'),
                                label='Choose snippet',
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


@register_snippet
class DomesticGrowthContent(index.Indexed, models.Model):
    content_id = models.CharField()
    title = models.CharField()
    description = RichTextField(blank=True)
    url = models.CharField(blank=True)

    panels = [
        FieldPanel('content_id'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('url'),
    ]

    search_fields = [
        index.AutocompleteField('title'),
    ]

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class StartingABusinessUser(TimeStampedModel):
    # never assume email is unique in this table as users can complete the triage in different
    # browsers / incognito mode
    email = models.CharField(max_length=255, null=True, blank=True)
    # the session_id is either a django session id from request.session.session_key or
    # in the case where a user has not accepted cookies a UUIDV4
    session_id = models.CharField(max_length=40, unique=True)
    sector_id = models.CharField(max_length=10, null=True, blank=True)
    dont_know_sector = models.BooleanField(default=False, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
