import logging

from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from wagtail.models import Page
from wagtail.rich_text import RichText, get_text_for_indexing

from core.models import MicrositePage
from domestic.models import ArticlePage
from export_academy.models import Booking, Event, Registration
from international_online_offer.models import TriageData, UserData

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
            if type(block_value) is RichText:
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


class MicrositePageSerializer(serializers.Serializer):
    expected_block_types = [
        'text',
        'cta',
        'image',
        'image_full_width',
        'video',
        'embed_video',
        'columns',
        'pull_quote',
        'links_block',
    ]

    def _get_microsite_body_content_for_search(self, obj: MicrositePage) -> str:
        """Selectively extract streamfield data from the blocks in ArticlePage's article_body streamfield.
        Strips markup from RichText objects, too."""

        streamfield_content = getattr(obj, 'page_body')

        searchable_items = []

        for streamchild in streamfield_content:
            if streamchild.block_type not in self.expected_block_types:
                logger.error(
                    f'Unhandled block type "{streamchild.block_type}" in '
                    'Microsite.page_body. Leaving out of search index content.'
                )
                continue

            block_value = streamchild.value
            if type(block_value) is RichText:
                searchable_items.append(get_text_for_indexing(block_value.__html__()))

            if streamchild.block_type == 'pull_quote':
                pull_quote_items = block_value.values()
                if any(pull_quote_items):
                    searchable_items.append(get_text_for_indexing(' '.join(pull_quote_items)))

        return ' '.join(searchable_items)

    def to_representation(self, obj):
        return {
            'id': ('dit:greatCms:Microsite:' + str(obj.id) + ':Update'),
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'dit:greatCms:Microsite',
                'id': 'dit:greatCms:Microsite:' + str(obj.id),
                'name': obj.page_title,
                'summary': obj.page_teaser,
                'content': self._get_microsite_body_content_for_search(obj),
                'url': f'https://www.great.gov.uk{obj.get_url()}',
                'locale_id': obj.locale_id
                # 'keywords': ' '.join(obj.tags.all().values_list('name', flat=True)),
            },
        }


class PageSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if isinstance(obj, ArticlePage):
            return ArticlePageSerializer(obj).data
        if isinstance(obj, MicrositePage):
            return MicrositePageSerializer(obj).data
        return CountryGuidePageSerializer(obj).data


class ActivityStreamExportAcademyEventSerializer(serializers.ModelSerializer):
    """
    UKEA's Event serializer for Activity Stream.
    """

    externalId = serializers.IntegerField(source='external_id')  # noqa: N815
    startDate = serializers.DateTimeField(source='start_date')  # noqa: N815
    endDate = serializers.DateTimeField(source='end_date')  # noqa: N815
    liveDate = serializers.DateTimeField(source='live')  # noqa: N815
    completeDate = serializers.DateTimeField(source='completed')  # noqa: N815
    types = TagListSerializerField()

    class Meta:
        model = Event
        fields = [
            'externalId',
            'name',
            'description',
            'format',
            'types',
            'link',
            'timezone',
            'startDate',
            'endDate',
            'liveDate',
            'completeDate',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportAcademy:event'
        type = 'Update'
        return {
            'id': f'{prefix}:{instance.id}:{type}',
            'type': f'{type}',
            'published': instance.modified.isoformat(),
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                'created': instance.created.isoformat(),
                'modified': instance.modified.isoformat(),
                **{f'{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamExportAcademyRegistrationSerializer(serializers.ModelSerializer):
    """
    UKEA's Registration serializer for Activity Stream.
    """

    externalId = serializers.IntegerField(source='external_id')  # noqa: N815
    firstName = serializers.CharField(source='first_name')  # noqa: N815
    lastName = serializers.CharField(source='last_name')  # noqa: N815
    hashedSsoId = serializers.CharField(source='hashed_sso_id')  # noqa: N815

    class Meta:
        model = Registration
        fields = ['externalId', 'hashedSsoId', 'email', 'firstName', 'lastName', 'data']

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportAcademy:registration'
        type = 'Update'
        return {
            'id': f'{prefix}:{instance.id}:{type}',
            'type': f'{type}',
            'published': instance.modified.isoformat(),
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                'created': instance.created.isoformat(),
                'modified': instance.modified.isoformat(),
                **{f'{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamExportAcademyBookingSerializer(serializers.ModelSerializer):
    """
    UKEA's Booking serializer for Activity Stream.
    """

    eventId = serializers.UUIDField(source='event_id')  # noqa: N815
    registrationId = serializers.UUIDField(source='registration_id')  # noqa: N815
    detailsViewed = serializers.DateTimeField(source='details_viewed')  # noqa: N815
    cookiesAcceptedOnDetailsView = serializers.BooleanField(source='cookies_accepted_on_details_view')  # noqa: N815

    class Meta:
        model = Booking
        fields = ['eventId', 'registrationId', 'status', 'detailsViewed', 'cookiesAcceptedOnDetailsView']

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportAcademy:booking'
        type = 'Update'
        return {
            'id': f'{prefix}:{instance.id}:{type}',
            'type': f'{type}',
            'published': instance.modified.isoformat(),
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                'created': instance.created.isoformat(),
                'modified': instance.modified.isoformat(),
                **{f'{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamExpandYourBusinessUserDataSerializer(serializers.ModelSerializer):
    """
    Expand Your Business User Data serializer for activity stream.

    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    hashedUuid = serializers.CharField(source='hashed_uuid')  # noqa: N815
    companyName = serializers.CharField(source='company_name')  # noqa: N815
    companyLocation = serializers.CharField(source='company_location')  # noqa: N815
    fullName = serializers.CharField(source='full_name')  # noqa: N815
    telephoneNumber = serializers.CharField(source='telephone_number')  # noqa: N815
    agreeTerms = serializers.BooleanField(source='agree_terms')  # noqa: N815
    agreeInfoEmail = serializers.BooleanField(source='agree_info_email')  # noqa: N815
    landingTimeframe = serializers.CharField(source='landing_timeframe')  # noqa: N815

    class Meta:
        model = UserData
        fields = [
            'id',
            'hashedUuid',
            'companyName',
            'companyLocation',
            'fullName',
            'role',
            'email',
            'telephoneNumber',
            'agreeTerms',
            'agreeInfoEmail',
            'landingTimeframe',
            'created',
            'modified',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:expandYourBusiness:userData'
        type = 'Update'

        return {
            'id': f'{prefix}:{instance.id}:{type}',
            'type': f'{type}',
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                **{f'{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamExpandYourBusinessTriageDataSerializer(serializers.ModelSerializer):
    """
    Expand Your Business Triage Data serializer for activity stream.

    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    hashedUuid = serializers.CharField(source='hashed_uuid')  # noqa: N815
    intentOther = serializers.CharField(source='intent_other')  # noqa: N815
    locationNone = serializers.BooleanField(source='location_none')  # noqa: N815
    spendOther = serializers.CharField(source='spend_other')  # noqa: N815
    isHighValue = serializers.BooleanField(source='is_high_value')  # noqa: N815

    class Meta:
        model = TriageData
        fields = [
            'id',
            'hashedUuid',
            'sector',
            'intent',
            'intentOther',
            'location',
            'locationNone',
            'hiring',
            'spend',
            'spendOther',
            'isHighValue',
            'created',
            'modified',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:expandYourBusiness:triageData'
        type = 'Update'

        return {
            'id': f'{prefix}:{instance.id}:{type}',
            'type': f'{type}',
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': prefix,
                **{f'{k}': v for k, v in super().to_representation(instance).items()},
            },
        }


class ActivityStreamCmsContentSerializer(serializers.ModelSerializer):
    """
    CMS content serializer for Activity Stream.
    """

    class Meta:
        model = Page
        fields = ['title', 'first_published_at', 'last_published_at']

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:cmsContent'
        subtype = 'domestic'
        operation = 'Update'
        return {
            'id': f'{prefix}:{subtype}:{instance.id}:{operation}',
            'type': f'{operation}',
            'published': instance.last_published_at.isoformat(),
            'object': {
                'id': f'{prefix}:{subtype}:{instance.id}',
                'type': prefix,
                'title': instance.title,
                'seoTitle': instance.seo_title,
                'url': instance.full_url,
                'searchDescription': instance.search_description,
                'firstPublishedAt': instance.first_published_at.isoformat(),
                'lastPublishedAt': instance.last_published_at.isoformat(),
                'contentTypeId': instance.content_type_id,
                # TODO: add content via page type serialisers
                'content': '',
            },
        }
