from storages.backends.s3boto3 import S3Boto3Storage

from botocore.exceptions import EndpointConnectionError
from wagtail.images.models import Image
from wagtail.documents.models import Document

from django.core.files.storage import (
    FileSystemStorage as OriginalFileSystemStorage
)

from core import models


class ImmutableFilesS3Boto3Storage(S3Boto3Storage):
    """Prevent deletion and replacing images from the bucket, as the bucket is
    used across multiple environments in order to facilitate copying of images
    from one environment to another.

    Extends:
        S3Boto3Storage

    """

    # cause the storage backend to prefix the filename if an image already
    # exists in the bucket with the same name.
    file_overwrite = False

    def delete(self, name):
        """Prevent deleting the image.

        The "image" exists as two things:

        1) The wagtai.wagtailImages.Image model in the db, which has the url
           of the actual image on s3.
        2) The actual image on s3.

        The user is allowed to delete 1, but we want to prevent the storage
        backend from actually deleting 2. We do that by preventing storage
        backend's delete from doing anything.

        """

        pass

    def get_object_by_path(self, path, model_class):
        try:
            object_summary = self.connection.ObjectSummary(
                bucket_name=self.bucket_name,
                key=path
            )
        except EndpointConnectionError:
            return None
        else:
            content_hash = object_summary.e_tag[1:-1]
            queryset = model_class.objects.filter(content_hash=content_hash)
            if queryset.exists():
                return queryset

    def get_image_by_path(self, image_path):
        queryset = self.get_object_by_path(image_path, models.ImageHash)
        if queryset:
            return queryset.first().image

    def get_document_by_path(self, document_path):
        queryset = self.get_object_by_path(document_path, models.DocumentHash)
        if queryset:
            return queryset.first().document


class FileSystemStorage(OriginalFileSystemStorage):
    def get_image_by_path(self, image_path):
        return Image.objects.filter(file=image_path).first()

    def get_document_by_path(self, document_path):
        return Document.objects.filter(file=document_path).first()