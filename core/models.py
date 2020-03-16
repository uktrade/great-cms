import hashlib
from django.db import models

from modelcluster.models import ClusterableModel, ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.core.models import Orderable
from wagtail.images.models import Image, AbstractImage, AbstractRendition
from wagtail.snippets.models import register_snippet


class AbstractObjectHash(models.Model):
    class Meta:
        abstract = True

    content_hash = models.CharField(max_length=1000)

    @staticmethod
    def generate_content_hash(field_file):
        filehash = hashlib.md5()
        field_file.open()
        filehash.update(field_file.read())
        field_file.close()
        return filehash.hexdigest()


class DocumentHash(AbstractObjectHash):
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )


class ImageHash(AbstractObjectHash):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )


class AltTextImage(AbstractImage):
    alt_text = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + ('alt_text',)


class Rendition(AbstractRendition):
    image = models.ForeignKey(AltTextImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'))


@register_snippet
class Tour(ClusterableModel):
    page = models.OneToOneField('wagtailcore.Page', on_delete=models.CASCADE, related_name='tour')
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    button_text = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('page'),
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('button_text'),
        MultiFieldPanel([InlinePanel('steps')], heading='Steps'),
    ]

    def __str__(self):
        return self.page.title


class TourStep(Orderable):
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    selector = models.CharField(max_length=255)
    tour = ParentalKey(Tour, on_delete=models.CASCADE, related_name='steps')

    panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('position'),
        FieldPanel('selector'),
    ]
