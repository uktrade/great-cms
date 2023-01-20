from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField

from core import blocks as core_blocks
from core.constants import RICHTEXT_FEATURES__REDUCED
from core.fields import single_struct_block_stream_field_factory
from core.models import TimeStampedModel
from domestic.models import BaseContentPage
from export_academy.cms_panels import ExportAcademyPagePanels


class Event(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    url = models.CharField(null=True, blank=True, max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    live = models.BooleanField(default=False)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('url'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('live'),
    ]


class ExportAcademyHomePage(ExportAcademyPagePanels, BaseContentPage):
    template = 'domestic/landing_page.html'

    parent_page_types = [
        'domestic.DomesticHomePage',  # TODO: once we've restructured, remove this permission
        'domestic.GreatDomesticHomePage',
    ]
    # hero
    hero_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_mobile_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_ipad_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_smalldesktop_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    hero_text = models.TextField(null=True, blank=True)
    hero_subtitle = models.TextField(null=True, blank=True)
    hero_cta_text = models.CharField(null=True, blank=True, max_length=255)
    hero_cta_url = models.CharField(null=True, blank=True, max_length=255)
    # Signed in versions
    hero_text_signedin = models.TextField(null=True, blank=True)
    hero_subtitle_signedin = models.TextField(null=True, blank=True)
    hero_cta_text_signedin = models.CharField(null=True, blank=True, max_length=255)
    hero_cta_url_signedin = models.CharField(null=True, blank=True, max_length=255)
    # EU exit chevrons StreamField WAS here in V1 - no longer the case

    # magna ctas
    magna_ctas_title = models.TextField(null=True, blank=True)
    magna_ctas_columns = single_struct_block_stream_field_factory(
        field_name='columns',
        block_class_instance=core_blocks.LinkWithImageAndContentBlockNoSource(),
        max_num=3,
        null=True,
        blank=True,
    )

    # how DIT helps
    how_dit_helps_title = models.TextField(null=True, blank=True)
    how_dit_helps_columns = single_struct_block_stream_field_factory(
        field_name='columns',
        block_class_instance=core_blocks.LinkWithImageAndContentBlock(),
        max_num=3,
        null=True,
        blank=True,
    )

    # Market access database
    madb_title = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='Title',
    )
    madb_image = models.ForeignKey(
        'core.AltTextImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Image',
        #
    )
    # equivalent of madb_image_alt field's now provided by core.AltTextImage

    madb_content = RichTextField(
        features=RICHTEXT_FEATURES__REDUCED,
        null=True,
        blank=True,
        verbose_name='Content',
    )
    madb_cta_text = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='CTA text',
    )
    madb_cta_url = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name='CTA URL',
    )

    # what's new
    what_is_new_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    what_is_new_pages = single_struct_block_stream_field_factory(
        field_name='pages',
        block_class_instance=core_blocks.LinkWithImageAndContentBlock(),
        max_num=6,
        null=True,
        blank=True,
    )

    campaign = single_struct_block_stream_field_factory(
        field_name='campaign',
        block_class_instance=core_blocks.CampaignBlock(),
        max_num=1,
        null=True,
        blank=True,
    )
