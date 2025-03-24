import sys
from time import sleep, time

import boto3
import sentry_sdk
from django.conf import settings
from django.core.management import BaseCommand

INVALIDATION_CHECK_INTERVAL_SECONDS = 10
INVALIDATION_CHECK_FAILURE_COUNT = 12


class Command(BaseCommand):
    help = 'Invalidate CDN Cache'

    def handle(self, *args, **options):
        if not settings.WAGTAILFRONTENDCACHE:
            sentry_sdk.capture_exception('Environment variable FRONTEND_CACHE_DISTRIBUTION_ID not set')
            sys.exit(1)

        sts_client = boto3.client('sts')
        role_arn = settings.CF_INVALIDATION_ROLE_ARN
        role_session_name = 'InvalidateCacheSession'

        assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name)
        credentials = assumed_role['Credentials']
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )

        client = session.client('cloudfront')

        for cloudfront_distribution_id in settings.WAGTAILFRONTENDCACHE:

            create_invalidation_response = client.create_invalidation(
                DistributionId=cloudfront_distribution_id,
                InvalidationBatch={
                    'Paths': {'Quantity': 1, 'Items': ['/*']},
                    'CallerReference': str(time()),
                },
            )

            invalidation_id = create_invalidation_response['Invalidation']['Id']
            invalidation_complete = False
            invalidation_check_count = 0

            while not invalidation_complete:
                if invalidation_check_count >= INVALIDATION_CHECK_FAILURE_COUNT:
                    sentry_sdk.capture_exception('Cache invalidation took too long, exiting')
                    sys.exit(1)

                sleep(INVALIDATION_CHECK_INTERVAL_SECONDS)

                get_invalidation_response = client.get_invalidation(
                    DistributionId=cloudfront_distribution_id, Id=invalidation_id
                )

                invalidation_status = get_invalidation_response['Invalidation']['Status'].lower()

                if invalidation_status == 'completed':
                    invalidation_complete = True
                    sentry_sdk.capture_message('Invalidation complete')
                    continue

                sentry_sdk.capture_message(f'Invalidation status: {invalidation_status}')

                invalidation_check_count += 1
