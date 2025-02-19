from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class CustomStorage(S3Boto3Storage):

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    if settings.DEBUG:
        custom_domain = '{0}/{1}'.format('localhost:4566', bucket_name)
