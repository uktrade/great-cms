import logging

from rest_framework import serializers
from wagtail.core.rich_text import RichText, get_text_for_indexing

from domestic.models import ArticlePage

logger = logging.getLogger(__name__)


class CountryGuidePageSerializer(serializers.Serializer):
    def _prep_richtext_for_indexing(self, rich_text_value: str) -> str:
        """Take an input HTML string and prep it for indexing. Specifically:
        * ensure there's a space between each HTML node, so that we get whitespace
          between strings that occur <h2>like</h2><p>this....</p>
        """
        # This is a super-naive pass, but we can trust that the HTML from a RichTextField
        # is clean, and a minimal change is good.
        return rich_text_value.replace('><', '> <')

    def to_representation(self, obj):
        return {
            'id': ('dit:greatCms:Article:' + str(obj.id) + ':Update'),
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'dit:greatCms:Article',
                'id': 'dit:greatCms:Article:' + str(obj.id),
                'name': obj.heading,
                'summary': obj.sub_heading,
                'content': self._prep_richtext_for_indexing(obj.section_one_body),
                'url': obj.get_absolute_url(),
                'keywords': ' '.join(obj.tags.all().values_list('name', flat=True)),
            },
        }


class ArticlePageSerializer(serializers.Serializer):
    expected_block_types = ['text', 'cta', 'image', 'Video', 'Columns', 'pull_quote']

    def _get_article_body_content_for_search(self, obj: ArticlePage) -> str:
        """Selectively extract streamfield data from the blocks in ArticlePage's article_body streamfield.
        Strips markup from RichText objects, too."""

        streamfield_content = getattr(obj, 'article_body')

        searchable_items = []

        for streamchild in streamfield_content:
            if streamchild.block_type not in self.expected_block_types:
                logger.error(
                    f'Unhandled block type "{streamchild.block_type}" in '
                    'ArticlePage.body_text. Leaving out of search index content.'
                )
                continue

            block_value = streamchild.value
            if type(block_value) == RichText:
                searchable_items.append(get_text_for_indexing(block_value.__html__()))

            if streamchild.block_type == 'pull_quote':
                pull_quote_items = block_value.values()
                if any(pull_quote_items):
                    searchable_items.append(get_text_for_indexing(' '.join(pull_quote_items)))

        return ' '.join(searchable_items)

    def to_representation(self, obj):
        return {
            'id': ('dit:greatCms:Article:' + str(obj.id) + ':Update'),
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'dit:greatCms:Article',
                'id': 'dit:greatCms:Article:' + str(obj.id),
                'name': obj.article_title,
                'summary': obj.article_teaser,
                'content': self._get_article_body_content_for_search(obj),
                'url': obj.get_absolute_url(),
            },
        }


class PageSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if isinstance(obj, ArticlePage):
            return ArticlePageSerializer(obj).data
        else:
            return CountryGuidePageSerializer(obj).data
