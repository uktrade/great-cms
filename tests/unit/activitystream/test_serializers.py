import json

import pytest

from activitystream.serializers import ArticlePageSerializer
from domestic.models import ArticlePage
from tests.unit.domestic.factories import ArticlePageFactory


@pytest.mark.django_db
def test_articleserializer_is_aware_of_all_streamfield_blocks(en_locale):

    available_blocks_for_article_body = [
        x.name for x in ArticlePage.article_body.field.stream_block.sorted_child_blocks()
    ]

    serializer = ArticlePageSerializer()
    # If this test fails, ArticlePageSerializer._get_article_body_content_for_search needs to be extended
    # to know what to do with StreamField blocks which have been added to ArticlePage.article_body
    assert sorted(serializer.expected_block_types) == sorted(available_blocks_for_article_body)


@pytest.mark.django_db
def test_articleserializer__get_article_body_content_for_search__simple(en_locale):

    article_instance = ArticlePageFactory(
        article_title='article test',
        article_teaser='Descriptive text',
        slug='article-test',
    )
    article_instance.article_body = json.dumps(
        [
            {
                'type': 'text',
                'value': '<p>Hello, World!</p>',
            }
        ]
    )
    article_instance.save()

    serializer = ArticlePageSerializer()
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert searchable_content == 'Hello, World!'


@pytest.mark.django_db
def test_articleserializer__get_article_body_content_for_search__pull_quote_entirely_included(en_locale):

    article_instance = ArticlePageFactory(
        article_title='article test',
        article_teaser='Descriptive text',
        slug='article-test',
    )
    article_instance.article_body = json.dumps(
        [
            {
                'type': 'text',
                'value': '<p>Hello, World!</p>',
            },
            {
                'type': 'pull_quote',
                'value': {
                    'quote': 'dummy quotestring',
                    'attribution': 'dummy attribution string',
                    'role': 'dummy role string',
                    'organisation': 'dummy organisation string',
                    'organisation_link': 'https://example.com/dummy-org-link',
                },
            },
        ]
    )
    article_instance.save()

    serializer = ArticlePageSerializer()
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert searchable_content == (
        'Hello, World! dummy quotestring dummy attribution string dummy role string '
        'dummy organisation string https://example.com/dummy-org-link'
    )


@pytest.mark.django_db
def test_articleserializer__get_article_body_content_for_search__more_complex_content(en_locale):

    article_instance = ArticlePageFactory(
        article_title='article test',
        article_teaser='Descriptive text',
        slug='article-test',
    )
    article_instance.article_body = json.dumps(
        [
            {
                'type': 'text',
                'value': '<p>Hello, World!</p>',
            },
            {
                'type': 'pull_quote',
                'value': {
                    'quote': 'dummy quotestring',
                    'attribution': 'dummy attribution string',
                    'role': 'dummy role string',
                    'organisation': 'dummy organisation string',
                    'organisation_link': 'https://example.com/dummy-org-link',
                },
            },
            {
                'type': 'text',
                'value': '<h2>Goodbye, World!</h2><p>Lorem <b>ipsum</b> <i>dolor</i> sit amet.</p>',
            },
        ]
    )
    article_instance.save()

    serializer = ArticlePageSerializer()
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert searchable_content == (
        'Hello, World! dummy quotestring dummy attribution string dummy role string '
        'dummy organisation string https://example.com/dummy-org-link '
        'Goodbye, World! Lorem ipsum dolor sit amet.'
    )


@pytest.mark.django_db
def test_articleserializer__get_article_body_content_for_search__no_content(en_locale):

    article_instance = ArticlePageFactory(
        article_title='article test',
        article_teaser='Descriptive text',
        slug='article-test',
    )
    article_instance.article_body = json.dumps(
        [
            {
                'type': 'text',
                'value': '',
            }
        ]
    )
    article_instance.save()

    serializer = ArticlePageSerializer()
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert searchable_content == ''
