import json

import pytest
from django.utils import timezone

from activitystream.serializers import (
    ActivityStreamExpandYourBusinessTriageDataSerializer,
    ActivityStreamExpandYourBusinessUserDataSerializer,
    ArticlePageSerializer,
    CountryGuidePageSerializer,
    ExportAcademyBookingSerializer,
    ExportAcademyEventSerializer,
    ExportAcademyRegistrationSerializer,
)
from domestic.models import ArticlePage
from international_online_offer.models import TriageData, UserData
from tests.unit.domestic.factories import ArticlePageFactory, CountryGuidePageFactory
from tests.unit.export_academy.factories import (
    BookingFactory,
    EventFactory,
    RegistrationFactory,
)


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


@pytest.mark.django_db
def test_ukea_event_serializer():
    instance = EventFactory()

    serializer = ExportAcademyEventSerializer()

    output = serializer.to_representation(instance)
    assert output == {
        'id': f'dit:exportAcademy:event:{instance.id}:Update',
        'type': 'Update',
        'published': instance.modified.isoformat(),
        'object': {
            'id': f'dit:exportAcademy:event:{instance.id}',
            'type': 'dit:exportAcademy:event',
            'created': instance.created.isoformat(),
            'modified': instance.modified.isoformat(),
            'completeDate': instance.completed.isoformat(),
            'description': instance.description,
            'endDate': instance.end_date.isoformat(),
            'format': instance.format,
            'link': instance.link,
            'liveDate': instance.live.isoformat(),
            'name': instance.name,
            'startDate': instance.start_date.isoformat(),
            'timezone': instance.timezone,
            'types': [type.name for type in instance.types.all()],
        },
    }


@pytest.mark.django_db
def test_ukea_registration_serializer():
    instance = RegistrationFactory()

    serializer = ExportAcademyRegistrationSerializer()

    output = serializer.to_representation(instance)
    assert output == {
        'id': f'dit:exportAcademy:registration:{instance.id}:Update',
        'type': 'Update',
        'published': instance.modified.isoformat(),
        'object': {
            'id': f'dit:exportAcademy:registration:{instance.id}',
            'type': 'dit:exportAcademy:registration',
            'created': instance.created.isoformat(),
            'modified': instance.modified.isoformat(),
            'email': instance.email,
            'firstName': instance.first_name,
            'lastName': instance.last_name,
            'data': instance.data,
        },
    }


@pytest.mark.django_db
def test_ukea_booking_serializer():
    instance = BookingFactory()

    serializer = ExportAcademyBookingSerializer()

    output = serializer.to_representation(instance)
    assert output == {
        'id': f'dit:exportAcademy:booking:{instance.id}:Update',
        'type': 'Update',
        'published': instance.modified.isoformat(),
        'object': {
            'id': f'dit:exportAcademy:booking:{instance.id}',
            'type': 'dit:exportAcademy:booking',
            'created': instance.created.isoformat(),
            'modified': instance.modified.isoformat(),
            'eventId': instance.event_id,
            'registrationId': instance.registration_id,
            'status': instance.status,
        },
    }


@pytest.mark.django_db
def test_eyb_user_serializer():
    instance = UserData()
    instance.id = 123
    instance.hashed_uuid = '456'
    instance.company_name = 'DBT'
    instance.company_location = 'UK'
    instance.full_name = 'Name'
    instance.role = 'Director'
    instance.email = 'email@email.com'
    instance.telephone_number = '07123567896'
    instance.agree_terms = True
    instance.agree_info_email = False
    instance.agree_info_telephone = False

    serializer = ActivityStreamExpandYourBusinessUserDataSerializer()

    output = serializer.to_representation(instance)
    expected = {
        'id': f'dit:expandYourBusiness:userData:{instance.id}:Update',
        'type': 'Update',
        'object': {
            'id': instance.id,
            'type': 'dit:expandYourBusiness:userData',
            'hashedUuid': instance.hashed_uuid,
            'companyName': instance.company_name,
            'companyLocation': instance.company_location,
            'fullName': instance.full_name,
            'role': instance.role,
            'email': instance.email,
            'telephoneNumber': instance.telephone_number,
            'agreeTerms': instance.agree_terms,
            'agreeInfoEmail': instance.agree_info_email,
            'agreeInfoTelephone': instance.agree_info_telephone,
        },
    }
    assert output == expected


@pytest.mark.django_db
def test_eyb_triage_serializer():
    instance = TriageData()

    instance.id = 123
    instance.hashed_uuid = '456'
    instance.sector = 'FOOD_AND_DRINK'
    instance.intent = ['SET_UP_NEW_PREMISES', 'SET_UP_A_NEW_DISTRIBUTION_CENTRE']
    instance.intent_other = 'OTHER'
    instance.location = 'WALES'
    instance.location_none = True
    instance.hiring = '1-10'
    instance.spend = '5000001-10000000'
    instance.spend_other = '456774'
    instance.is_high_value = True

    serializer = ActivityStreamExpandYourBusinessTriageDataSerializer()
    output = serializer.to_representation(instance)
    expected = {
        'id': f'dit:expandYourBusiness:triageData:{instance.id}:Update',
        'type': 'Update',
        'object': {
            'id': instance.id,
            'type': 'dit:expandYourBusiness:triageData',
            'hashedUuid': instance.hashed_uuid,
            'sector': instance.sector,
            'intent': instance.intent,
            'intentOther': instance.intent_other,
            'location': instance.location,
            'locationNone': instance.location_none,
            'hiring': instance.hiring,
            'spend': instance.spend,
            'spendOther': instance.spend_other,
            'isHighValue': instance.is_high_value,
        },
    }
    print(output)
    print(output)
    assert output == expected
