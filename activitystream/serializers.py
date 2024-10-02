import logging

from rest_framework import serializers
from taggit.serializers import TagListSerializerField
from wagtail.models import Page
from wagtail.rich_text import RichText, get_text_for_indexing

from core.models import (
    CsatUserFeedback as WhereToExportCsatUserFeedback,
    GreatMedia,
    MicrositePage,
)
from domestic.models import ArticlePage
from export_academy.models import (
    Booking,
    CsatUserFeedback,
    Event,
    Registration,
    VideoOnDemandPageTracking,
)
from exportplan.models import CsatUserFeedback as ExportPlanCsatUserFeedback
from find_a_buyer.models import CsatUserFeedback as FindABuyerCsatUserFeedback
from international_online_offer.models import CsatFeedback, TriageData, UserData
from learn.models import CsatUserFeedback as LearnToExportCsatUserFeedback

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
            'id': 'dit:greatCms:Article:' + str(obj.id) + ':Update',
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
    expected_block_types = [
        'text',
        'cta',
        'data_table',
        'image',
        'Video',
        'Columns',
        'pull_quote',
        'content_module',
        'mounted_blocks',
    ]

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
            'id': 'dit:greatCms:Article:' + str(obj.id) + ':Update',
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
        'table',
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
            'id': 'dit:greatCms:Microsite:' + str(obj.id) + ':Update',
            'type': 'Update',
            'published': obj.last_published_at.isoformat('T'),
            'object': {
                'type': 'dit:greatCms:Microsite',
                'id': 'dit:greatCms:Microsite:' + str(obj.id),
                'name': obj.page_title,
                'summary': obj.page_teaser,
                'content': self._get_microsite_body_content_for_search(obj),
                'url': f'https://www.great.gov.uk{obj.get_url()}',
                'locale_id': obj.locale_id,
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
    companyWebsite = serializers.CharField(source='company_website')  # noqa: N815
    dunsNumber = serializers.CharField(source='duns_number')  # noqa: N815
    addressLine1 = serializers.CharField(source='address_line_1')  # noqa: N815
    addressLine2 = serializers.CharField(source='address_line_2')  # noqa: N815
    town = serializers.CharField()  # noqa: N815
    county = serializers.CharField()  # noqa: N815
    postcode = serializers.CharField()  # noqa: N815

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
            'companyWebsite',
            'dunsNumber',
            'addressLine1',
            'addressLine2',
            'town',
            'county',
            'postcode',
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
    locationCity = serializers.CharField(source='location_city')  # noqa: N815
    sectorSub = serializers.CharField(source='sector_sub')  # noqa: N815
    sectorSubSub = serializers.CharField(source='sector_sub_sub')  # noqa: N815
    sectorID = serializers.CharField(source='sector_id')  # noqa: N815

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
            'locationCity',
            'sectorSub',
            'sectorSubSub',
            'sectorID',
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


class ActivityStreamExpandYourBusinessCsatFeedbackDataSerializer(serializers.ModelSerializer):
    """
    Expand Your Business CSAT Feedback Data serializer for activity stream.

    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815
    site_intentions_other_detail = serializers.CharField(source='site_intentions_other')  # noqa: N815

    class Meta:
        model = CsatFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issue',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
            'site_intentions',
            'site_intentions_other_detail',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:expandYourBusiness:csatFeedbackData'
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


class GreatMediaSerializer(serializers.ModelSerializer):
    """
    GreatMedia serializer for Activity Stream.
    """

    videoId = serializers.UUIDField(source='id')  # noqa: N815
    videoTitle = serializers.CharField(source='title')  # noqa: N815

    class Meta:
        model = GreatMedia
        fields = ['videoId', 'videoTitle']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Registration serializer for Activity Stream.
    """

    registrationHashedSsoId = serializers.CharField(source='hashed_sso_id')  # noqa: N815

    class Meta:
        model = Registration
        fields = ['registrationHashedSsoId']


class ActivityStreamExportAcademyVideoOnDemandPageTrackingSerializer(serializers.ModelSerializer):
    """
    UKEA's VideoOnDemandPageTracking serializer for Activity Stream.
    """

    userEmail = serializers.EmailField(source='user_email')  # noqa: N815
    hashedUuid = serializers.CharField(source='hashed_uuid')  # noqa: N815
    region = serializers.CharField()  # noqa: N815
    companyName = serializers.CharField(source='company_name')  # noqa: N815
    companyPostcode = serializers.CharField(source='company_postcode')  # noqa: N815
    companyPhone = serializers.CharField(source='company_phone')  # noqa: N815
    detailsViewed = serializers.DateTimeField(source='details_viewed')  # noqa: N815
    cookiesAcceptedOnDetailsView = serializers.BooleanField(source='cookies_accepted_on_details_view')  # noqa: N815
    eventId = serializers.UUIDField(source='event_id')  # noqa: N815
    bookingId = serializers.UUIDField(source='booking_id')  # noqa: N815
    registrationId = serializers.UUIDField(source='registration_id')  # noqa: N815
    video = GreatMediaSerializer(many=False)
    registration = RegistrationSerializer(many=False)

    class Meta:
        model = VideoOnDemandPageTracking
        fields = [
            'userEmail',
            'hashedUuid',
            'region',
            'companyName',
            'companyPostcode',
            'companyPhone',
            'detailsViewed',
            'cookiesAcceptedOnDetailsView',
            'eventId',
            'bookingId',
            'registrationId',
            'video',
            'registration',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportAcademy:videoondemandpagetracking'
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
                'userEmail': instance.user_email,
                'hashedUuid': instance.hashed_uuid,
                'region': instance.region,
                'companyName': instance.company_name,
                'companyPostcode': instance.company_postcode,
                'companyPhone': instance.company_phone,
                'detailsViewed': instance.details_viewed,
                'cookiesAcceptedOnDetailsView': instance.cookies_accepted_on_details_view,
                'eventId': instance.event.id,
                'bookingId': instance.booking.id if instance.booking else None,
                'registrationId': instance.registration.id if instance.registration else None,
                'registrationHashedSsoId': instance.registration.hashed_sso_id if instance.registration else None,
                'videoId': instance.video.id if instance.video else None,
                'videoTitle': instance.video.title if instance.video else None,
            },
        }


class ActivityStreamExportAcademyCsatUserFeedbackDataSerializer(serializers.ModelSerializer):
    """
    UKEA's CSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815

    class Meta:
        model = CsatUserFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportAcademy:csatFeedbackData'
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


class ActivityStreamWhereToExportCsatUserFeedbackDataSerializer(serializers.ModelSerializer):
    """
    Where to Export's CSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815

    class Meta:
        model = WhereToExportCsatUserFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:whereToExport:csatFeedbackData'
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


class ActivityStreamFindABuyerCsatUserFeedbackDataSerializer(serializers.ModelSerializer):
    """
    Find A Buyer CSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815

    class Meta:
        model = FindABuyerCsatUserFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:findABuyer:csatFeedbackData'
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


class ActivityStreamLearnToExportCsatUserFeedbackDataSerializer(serializers.ModelSerializer):
    """
    Learn To Export CSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815

    class Meta:
        model = LearnToExportCsatUserFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:learnToExport:csatFeedbackData'
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


class ActivityStreamExportPlanCsatUserFeedbackDataSerializer(serializers.ModelSerializer):
    """
    Make an Export Plan CSAT Feedback Data serializer for activity stream.
    """

    feedback_submission_date = serializers.DateTimeField(source='created')  # noqa: N815
    url = serializers.CharField(source='URL')  # noqa: N815

    class Meta:
        model = ExportPlanCsatUserFeedback
        fields = [
            'id',
            'feedback_submission_date',
            'url',
            'user_journey',
            'satisfaction_rating',
            'experienced_issues',
            'other_detail',
            'service_improvements_feedback',
            'likelihood_of_return',
        ]

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:exportPlan:csatFeedbackData'
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
