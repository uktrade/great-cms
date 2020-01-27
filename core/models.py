import hashlib
from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition


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
