from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from wagtail.documents.models import AbstractDocument

from core.utils import get_mime_type


def clean(self):
    """
    Added monkey patch to improvised existing clean method for validation of file type by
    extra check on mimetype of the file.

    More info : https://docs.djangoproject.com/en/3.1/ref/validators/#fileextensionvalidator
    """
    mimetype = get_mime_type(self.file)
    allowed_extensions = getattr(settings, 'WAGTAILDOCS_EXTENSIONS', None)
    allowed_mimetypes = getattr(settings, 'WAGTAILDOCS_MIME_TYPES', None)

    if allowed_extensions:
        validate = FileExtensionValidator(allowed_extensions)
        validate(self.file)

    if allowed_mimetypes and mimetype not in allowed_mimetypes:
        raise ValidationError(message="File\'s mime type not allowed.", code='invalid')


AbstractDocument.clean = clean
