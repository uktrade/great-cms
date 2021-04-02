import json

import pytest

from activitystream.serializers import ArticlePageSerializer
from tests.unit.domestic.factories import ArticlePageFactory


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
def test_articleserializer__get_article_body_content_for_search__show_pull_quotes_skipped(en_locale):

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
                    'quote': 'dummy_quote',
                    'attribution': 'dummy_attribution',
                    'role': 'dummy_role',
                    'organisation': 'dummy_organisation',
                    'organisation_link': 'dummy_organisation_link',
                },
            },
        ]
    )
    article_instance.save()

    serializer = ArticlePageSerializer()
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert searchable_content == 'Hello, World!'


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
                    'quote': 'dummy_quote',
                    'attribution': 'dummy_attribution',
                    'role': 'dummy_role',
                    'organisation': 'dummy_organisation',
                    'organisation_link': 'dummy_organisation_link',
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

    assert searchable_content == 'Hello, World! Goodbye, World! Lorem ipsum dolor sit amet.'


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
