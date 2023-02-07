import json

import pytest
from django.utils import timezone

from activitystream.serializers import ArticlePageSerializer, CountryGuidePageSerializer
from domestic.models import ArticlePage
from tests.unit.domestic.factories import ArticlePageFactory, CountryGuidePageFactory


@pytest.mark.django_db
def test_articleserializer_is_aware_of_all_streamfield_blocks(en_locale):
    # If this test fails, ArticlePageSerializer._get_article_body_content_for_search needs to be extended
    # to know what to do with StreamField blocks which have been added to ArticlePage.article_body

    available_blocks_for_article_body = [
        x.name for x in ArticlePage.article_body.field.stream_block.sorted_child_blocks()
    ]

    serializer = ArticlePageSerializer()
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


@pytest.mark.django_db
def test_articleserializer__get_article_body_content_for_search__skipping_unknown_block(
    en_locale,
    caplog,
):
    # Rather than add a new block to the streamfield and then confirm its skipped, we can test
    # the core code by removing a block type from the list that the serializer knows about

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
    serializer.expected_block_types = [
        'pull_quote',
    ]  # ie, 'text' is not in here

    assert len(caplog.records) == 0
    searchable_content = serializer._get_article_body_content_for_search(article_instance)

    assert len(caplog.records) == 2
    for i in range(2):
        assert caplog.records[i].message == (
            'Unhandled block type "text" in ArticlePage.body_text. Leaving out of search index content.'
        )
        assert caplog.records[i].levelname == 'ERROR'

    assert searchable_content == (
        # Only the pull-quote's content is here:
        'dummy quotestring dummy attribution string dummy role string '
        'dummy organisation string https://example.com/dummy-org-link'
    )


@pytest.mark.django_db
def test_countryguidepageserializer__prep_richtext_for_indexing(domestic_homepage):
    instance = CountryGuidePageFactory(
        parent=domestic_homepage,
        section_one_body=(
            '<h2>header here</h2><p>Para content here.</p><p></p><h3>h3 content here</h3><p>more text</p>'
        ),
    )

    serializer = CountryGuidePageSerializer()

    output = serializer._prep_richtext_for_indexing(instance.section_one_body)
    assert output == (
        '<h2>header here</h2> <p>Para content here.</p> <p> </p> <h3>h3 content here</h3> <p>more text</p>'
    )


@pytest.mark.django_db
def test_countryguidepageserializer(domestic_homepage):
    instance = CountryGuidePageFactory(
        parent=domestic_homepage,
        sub_heading='Here is the subheading',
        section_one_body=('<h2>header here</h2><p>Para content here.</p>'),
    )
    instance.last_published_at = timezone.now()
    instance.save()

    serializer = CountryGuidePageSerializer()

    output = serializer.to_representation(instance)
    assert output == {
        'id': f'dit:greatCms:Article:{instance.id}:Update',
        'type': 'Update',
        'published': instance.last_published_at.isoformat('T'),
        'object': {
            'type': 'dit:greatCms:Article',
            'id': f'dit:greatCms:Article:{instance.id}',
            'name': 'Heading for Country',
            'summary': 'Here is the subheading',
            'content': '<h2>header here</h2> <p>Para content here.</p>',
            'url': instance.get_absolute_url(),
            'keywords': '',
        },
    }
