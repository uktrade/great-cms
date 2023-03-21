from django.db import models
<<<<<<< HEAD
<<<<<<< HEAD
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey
from taggit.models import TagBase, TaggedItemBase
=======
from modelcluster.models import ParentalKey
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
>>>>>>> 8569f1312 (Feature/ioo 437 articles (#2045))
=======
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey
from taggit.models import TagBase, TaggedItemBase
>>>>>>> fd365a2a7 (Fix font style for input text and fix for tags not saving (#2053))
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


<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> fd365a2a7 (Fix font style for input text and fix for tags not saving (#2053))
class IOOArticleTag(TagBase):
    """IOO article tag for filtering out content based on triage answers."""

    class Meta:
        verbose_name = 'IOO article tag for link to triage answer'
        verbose_name_plural = 'IOO article tags for links to triage answers'


<<<<<<< HEAD
class IOOArticlePageTag(TaggedItemBase):
    tag = models.ForeignKey(IOOArticleTag, related_name='ioo_tagged_articles', on_delete=models.CASCADE)
    content_object = ParentalKey('international_online_offer.IOOArticlePage', related_name='ioo_article_tagged_items')
=======
class IOOArticlePageTag(TaggedItemBase):
    content_object = ParentalKey('international_online_offer.IOOArticlePage', related_name='tagged_items')
>>>>>>> 8569f1312 (Feature/ioo 437 articles (#2045))
=======
class IOOArticlePageTag(TaggedItemBase):
    tag = models.ForeignKey(IOOArticleTag, related_name='ioo_tagged_articles', on_delete=models.CASCADE)
    content_object = ParentalKey('international_online_offer.IOOArticlePage', related_name='ioo_article_tagged_items')
>>>>>>> fd365a2a7 (Fix font style for input text and fix for tags not saving (#2053))


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
<<<<<<< HEAD
<<<<<<< HEAD
    tags = ClusterTaggableManager(through=IOOArticlePageTag, blank=True, verbose_name='Article Tags')
=======
    tags = TaggableManager(through=IOOArticlePageTag, blank=True)
>>>>>>> 8569f1312 (Feature/ioo 437 articles (#2045))
=======
    tags = ClusterTaggableManager(through=IOOArticlePageTag, blank=True, verbose_name='Article Tags')
>>>>>>> fd365a2a7 (Fix font style for input text and fix for tags not saving (#2053))
    content_panels = CMSGenericPage.content_panels + [
        FieldPanel('article_title'),
        FieldPanel('article_subheading'),
        FieldPanel('article_teaser'),
        ImageChooserPanel('article_image'),
        StreamFieldPanel('article_body'),
        FieldPanel('tags'),
    ]
