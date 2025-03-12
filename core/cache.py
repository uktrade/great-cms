from django.conf import settings
from wagtail.contrib.frontend_cache.backends import CloudfrontBackend


class GreatCloudfrontBackend(CloudfrontBackend):
    def __init__(self, params):
        params = self._get_params(params)
        super().__init__(params)

    def _create_invalidation(self, distribution_id, paths):
        paths = list(paths)
        super()._create_invalidation(distribution_id, paths)

    def _get_params(self, params):
        import boto3
        boto3.set_stream_logger('')
        role_arn = settings.CF_INVALIDATION_ROLE_ARN
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='CloudFrontInvalidationSession')
        credentials = assumed_role['Credentials']
        params['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
        params['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
        params['AWS_SESSION_TOKEN'] = credentials['SessionToken']
        return params
