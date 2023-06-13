import logging

from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from wagtail.rich_text import RichText, get_text_for_indexing

from domestic.models import ArticlePage
from export_academy.models import Booking, Event
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
    expected_block_types = ['text', 'cta', 'image', 'Video', 'Columns', 'pull_quote', 'form']

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


class ExportAcademyEventSerializer(serializers.ModelSerializer):
    """
    UKEA's Event serializer for Activity Stream.
    """

    startDate = serializers.DateTimeField(source='start_date')  # noqa: N815
    endDate = serializers.DateTimeField(source='end_date')  # noqa: N815
    liveDate = serializers.DateTimeField(source='live')  # noqa: N815
    completeDate = serializers.DateTimeField(source='completed')  # noqa: N815
    types = TagListSerializerField()

    class Meta:
        model = Event
        fields = [
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


class ExportAcademyBookingSerializer(serializers.ModelSerializer):
    """
    UKEA's Booking serializer for Activity Stream.
    """

    eventId = serializers.UUIDField(source='event_id')  # noqa: N815
    registrationId = serializers.UUIDField(source='registration_id')  # noqa: N815

    class Meta:
        model = Booking
        fields = ['eventId', 'registrationId', 'status']

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

    hashedUuid = serializers.CharField(source='hashed_uuid')
    companyName = serializers.CharField(source='company_name')
    companyLocation = serializers.CharField(source='company_location')
    fullName = serializers.CharField(source='full_name')
    telephoneNumber = serializers.CharField(source='telephone_number')
    agreeTerms = serializers.BooleanField(source='agree_terms')
    agreeInfoEmail = serializers.BooleanField(source='agree_info_email')
    agreeInfoTelephone = serializers.BooleanField(source='agree_info_telephone')

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
            'agreeInfoTelephone',
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

    hashedUuid = serializers.CharField(source='hashed_uuid')
    intentOther = serializers.CharField(source='intent_other')
    locationNone = serializers.BooleanField(source='location_none')
    spendOther = serializers.CharField(source='spend_other')
    isHighValue = serializers.BooleanField(source='is_high_value')

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
