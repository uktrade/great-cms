from wagtail.contrib.frontend_cache.backends import CloudfrontBackend


class GreatCloudfrontBackend(CloudfrontBackend):
    def _create_invalidation(self, distribution_id, paths):
        paths = list(paths)
        super()._create_invalidation(distribution_id, paths)
