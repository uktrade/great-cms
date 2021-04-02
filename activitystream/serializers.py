import logging

from rest_framework import serializers
from wagtail.core.rich_text import RichText, get_text_for_indexing

from domestic.models import ArticlePage

logger = logging.getLogger(__name__)


class CountryGuidePageSerializer(serializers.Serializer):
    def to_representation(self, obj):
        return {
            'id': ('dit:greatCms:Article:' + str(obj.id) + ':Update'),
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'Article',
                'id': 'dit:greatCms:Article:' + str(obj.id),
                'name': obj.heading,
                'summary': obj.sub_heading,
                'content': obj.section_one_body,
                'url': obj.get_absolute_url(),
                'keywords': ' '.join(obj.tags.all().values_list('name', flat=True)),
            },
        }


class ArticlePageSerializer(serializers.Serializer):
    def _get_article_body_content_for_search(self, obj: ArticlePage) -> str:
        """Selectively extract streamfield data from the ArticlePage's 'text' blocks,
        skipping pull quotes entirely.

        Strips markup from RichText objects, too."""

        expected_block_types = ('text', 'pull_quote')

        streamfield_content = getattr(obj, 'article_body')

        searchable_items = []

        for streamchild in streamfield_content:
            if streamchild.block_type not in expected_block_types:
                logger.error(
                    f'Unhandled block type {streamchild.block_type} in '
                    'ArticlePage.body_text - leaving out of search index.'
                )
                continue

            block_value = streamchild.value
            if type(block_value) == RichText:
                searchable_items.append(get_text_for_indexing(block_value.__html__()))

        return ' '.join(searchable_items)

    def to_representation(self, obj):

        return {
            'id': ('dit:greatCms:Article:' + str(obj.id) + ':Update'),
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'Article',
                'id': 'dit:greatCms:Article:' + str(obj.id),
                'name': obj.article_title,
                'summary': obj.article_teaser,
                'content': self._get_article_body_content_for_search(obj),
                'url': obj.get_absolute_url(),
            },
        }


class MarketingArticlePageSerializer(ArticlePageSerializer):
    pass


class PageSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if isinstance(obj, ArticlePage):
            return ArticlePageSerializer(obj).data
        else:  # CountryGuidePage
            return CountryGuidePageSerializer(obj).data
