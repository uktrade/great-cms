import datetime
import json
import logging
import uuid
from urllib.parse import urlparse

import boto3
import readtime
import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.files.storage import DefaultStorage
from django.db import models as django_models
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from great_components.helpers import add_next
from wagtail import hooks
from wagtail.admin.menu import DismissibleMenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.admin.views.pages.bulk_actions.page_bulk_action import PageBulkAction
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import ModelViewSet, ModelViewSetGroup
from wagtail_transfer.field_adapters import FieldAdapter
from wagtail_transfer.files import File as WTFile, FileTransferError
from wagtail_transfer.models import ImportedFile

from core import constants, mixins, views
from core.models import (
    CountryTag,
    MicrositePage,
    PersonalisationRegionTag,
    PersonalisationTradingBlocTag,
    SectorTag,
    TypeOfExportTag,
)
from core.views import AltImageChooserViewSet
from domestic.models import ArticlePage, CountryGuidePage
from .rich_text import (
    AnchorIdentifierLinkHandler,
    AnchorIndentifierEntityElementHandler,
    anchor_identifier_entity_decorator,
)

logger = logging.getLogger(__name__)

SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT = 'LESSON_PAGE_SHOW_GENERIC_CONTENT'
exportplan_templates = ['exportplan/automated_list_page.html', 'exportplan/dashboard_page.html']

# Make an S3 API available to us
s3 = boto3.resource('s3')


@hooks.register('before_serve_page')
def anonymous_user_required(page, request, serve_args, serve_kwargs):
    if isinstance(page, mixins.AnonymousUserRequired):
        if request.user.is_authenticated:
            return redirect(page.anonymous_user_required_redirect_url)


@hooks.register('before_serve_page')
def authenticated_user_required(page, request, serve_args, serve_kwargs):
    if isinstance(page, mixins.AuthenticatedUserRequired):
        if not request.user.is_authenticated:
            onward_destination = request.get_full_path()  # this includes any querystrings
            dest = page.authenticated_user_required_redirect_url
            if onward_destination:
                dest += f'?{REDIRECT_FIELD_NAME}={onward_destination}'

            return redirect(dest)


@hooks.register('before_serve_page')
def login_required_signup_wizard(page, request, serve_args, serve_kwargs):
    if not settings.FEATURE_DEA_V2:
        if page.template == 'learn/detail_page.html' and request.user.is_anonymous:  # pragma: no cover
            # opting out of personalised content 'forever' - not just this request.
            if 'show-generic-content' in request.GET:
                request.session[SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT] = True

            if not request.session.get(SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT):  # pragma: no cover
                signup_url = reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START})
                url = add_next(destination_url=signup_url, current_url=request.get_full_path())
                return redirect(url)


def _update_data_for_appropriate_version(page: Page, force_page_update: bool, data_to_update: dict) -> None:
    """For a given Page instance, use the provided data to update either:
    * its latest revision ONLY, if there are ONLY unpublished changes
    (ie, its a Draft)
    or
    * the latest revision AND the live page, if the revision is the one
    that became the live page (ie the Live page does NOT have unpublished
    changes)
    or
    * we're forcing updates to the actual Page and not its revision JSON
    (eg, because the Live page has just been created so has no
    unpublished changes, but we still want to update it with data_to_update)
    """
    latest_revision = page.get_latest_revision()

    if isinstance(latest_revision.content, str):
        json_object = json.loads(latest_revision.content)
        latest_revision.content = json_object

    latest_revision_json = latest_revision.content

    for key, value in data_to_update.items():
        # We need to watch out for the timedelta, because it serialises to
        # a different format (PxDTxxHxxMxxS) by default
        if isinstance(value, datetime.timedelta):
            value = str(value)
        latest_revision_json[key] = value

    latest_revision.content = latest_revision_json
    latest_revision.save()

    if force_page_update or (not page.has_unpublished_changes):
        # This update()-based approach is awkward but we want to update the
        # Page record without any side effects via save() etc
        queryset_for_page = type(page).objects.filter(id=page.id)
        queryset_for_page.update(**data_to_update)


@hooks.register('after_create_page')
def set_read_time__after_create_page(request, page):
    # Runs after a page is created, whether draft or published
    _set_read_time(request, page, is_post_creation=True)


@hooks.register('after_edit_page')
def set_read_time__after_edit_page(request, page):
    # Runs after a page is edited, whether draft or published
    _set_read_time(request, page)


def _set_read_time(request, page, is_post_creation=False):
    if hasattr(page, 'estimated_read_duration'):
        html = render_to_string(page.template, {'page': page, 'request': request})
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.body.find_all(['script', 'noscript', 'link', 'style', 'meta', 'header']):
            tag.decompose()
        # Get the readtime of the main content section of the page (excluding header/footer)
        reading_seconds = readtime.of_html(str(soup.find('main'))).seconds
        video_nodes = soup.find_all('video', attrs={constants.VIDEO_DURATION_DATA_ATTR_NAME: True})
        watching_seconds = sum(
            [int(node.get(constants.VIDEO_DURATION_DATA_ATTR_NAME, 0).replace('.0', '')) for node in video_nodes]
        )
        seconds = reading_seconds + watching_seconds

        _update_data_for_appropriate_version(
            page=page,
            force_page_update=is_post_creation,
            data_to_update={'estimated_read_duration': datetime.timedelta(seconds=seconds)},
        )


class S3WagtailTransferFile(WTFile):
    """Subclass of File that knows how to transfer() using an
    S3 to S3 copy"""

    def __init__(self, local_filename, size, hash_, source_url, **kwargs):
        super().__init__(local_filename=local_filename, size=size, hash=hash_, source_url=source_url)

        self.source_bucket = kwargs['source_bucket']
        self.source_key = kwargs['source_key']

    def transfer(self):
        # NB: This will only work if the source file is publicly readable
        copy_source = {'Bucket': self.source_bucket, 'Key': self.source_key}

        try:
            s3.meta.client.copy(copy_source, settings.AWS_STORAGE_BUCKET_NAME, self.local_filename)
        except (
            boto3.exceptions.RetriesExceededError,
            boto3.exceptions.S3UploadFailedError,
            ValueError,
            # This may not be exhaustive - we'll have to expand as required
            # or just catch Exception
        ) as ex:
            logger.exception(ex)
            raise FileTransferError(ex)

        return ImportedFile.objects.create(
            file=self.local_filename,
            source_url=self.source_url,
            hash=self.hash,
            size=self.size,
        )


class S3FileFieldAdapter(FieldAdapter):
    """Custom adapter that handles file fields when using AWS S3

    NOTE that this will only work for transfers within the same Region
    """

    def _get_relevant_s3_meta(self, field_value) -> dict:
        """Returns relevant metadata from S3 in a single data structure,
        cleaned up and with one network request."""

        # TODO: cache this? NB: the adapter itself is cached/persisted
        # so we can't put state on it

        _object_summary = s3.ObjectSummary(
            field_value.storage.bucket.name,  # bucket
            field_value.name,  # key
        )
        return {'size': _object_summary.size, 'hash': self._get_file_hash(_object_summary)}

    def _get_file_hash(self, object_summary) -> str:
        """Uses the object's eTag as a hash, avoiding the need to
        download and hash the actual file"""

        # IMPORTANT: The ETag from S3 may not be reliable/consistent
        # if the file ended up being multi-part uploaded. If that's the
        # case, we'll get a 'cache miss' and end up doing redundant work
        #
        # * https://boto3.amazonaws.com/v1/documentation/api/latest/
        #       reference/services/s3.html#S3.ObjectSummary.e_tag
        # * https://boto3.amazonaws.com/v1/documentation/api/latest/
        #       reference/services/s3.html#S3.Object.initiate_multipart_upload
        #
        # Also note that the ETags are wrapped in quotes, as per RFC:
        # https://tools.ietf.org/html/rfc2616#section-14.19 but we'll drop
        # them here to avoid noise in our hash

        return object_summary.e_tag.replace('"', '')

    def _get_imported_file_bucket_and_key(self, imported_file_url) -> tuple:
        """From the URL for the imported file, work out what its
        S3 bucket and key are, so we can make an API call to copy it.

        Here, we're trusting that our buckets are consistenty configured to be
        subdomains + constants.AWS_S3_MAIN_HOSTNAME
        """

        source = urlparse(imported_file_url)

        bucket_name = source.netloc

        for _hostname in constants.AWS_S3_MAIN_HOSTNAME_OPTIONS:
            if _hostname in bucket_name:
                _target = f'.{_hostname}'
                bucket_name = bucket_name.replace(_target, '')
                continue

        key_name = source.path[1:] if source.path.startswith('/') else source.path
        return bucket_name, key_name

    def serialize(self, instance):
        value = self.field.value_from_object(instance)
        if not value:
            return None

        # This adapter is only used when files are on S3, so there's no need
        # to prepend MEDIA_URL to `url` (which the default FileAdapter does)
        url = value.url

        _s3_object_metadata = self._get_relevant_s3_meta(field_value=value)

        return {
            'download_url': url,
            'size': _s3_object_metadata['size'],
            'hash': _s3_object_metadata['hash'],
        }

    def populate_field(self, instance, value, context):
        """Check if the field's file needs to be imported, and if so, do so."""

        # `value` is the output of self.serialize() - either a dict or None
        if not value:
            return None

        source_file_url = value['download_url']
        source_file_hash = value['hash']
        source_file_size = value['size']

        imported_file = context.imported_files_by_source_url.get(source_file_url)
        if imported_file is None:
            logger.info('File from %s has not already been imported: reimporting', source_file_url)

            existing_file = self.field.value_from_object(instance)
            if existing_file:
                logger.info('File exists. Comparing hashes with source file and existing file')
                _s3_object_metadata = self._get_relevant_s3_meta(field_value=existing_file)
                existing_file_hash = _s3_object_metadata['hash']
                if existing_file_hash == source_file_hash:
                    # File not changed, so don't bother updating it
                    logger.info('Matching hashes, so no need to import')
                    return

            # Generate a safe, new filename for the destination bucket, so avoid overwrites
            source_bucket, source_key = self._get_imported_file_bucket_and_key(source_file_url)

            target_filename = DefaultStorage().get_available_name(source_key)

            _file = S3WagtailTransferFile(
                local_filename=target_filename,
                size=source_file_size,
                hash_=source_file_hash,
                source_url=source_file_url,
                source_bucket=source_bucket,
                source_key=source_key,
            )
            try:
                logger.info('Attempting to copy file from %s, S3-to-S3', source_file_url)
                imported_file = _file.transfer()
            except FileTransferError as ex:
                logger.exception('Failed to transfer: %s', ex)
                return None

            context.imported_files_by_source_url[_file.source_url] = imported_file

        # This is standard behaviour from the base FileAdapter:
        value = imported_file.file.name
        getattr(instance, self.field.get_attname()).name = value

        logger.info('File copied to destination')


@hooks.register('register_field_adapters')
def register_s3_media_file_adapter():
    """For all FileFields in our application, use our custom S3 one
    to handle transfers
    """

    extra_adapters = {}

    if settings.USER_MEDIA_ON_S3:
        extra_adapters.update(
            {
                django_models.FileField: S3FileFieldAdapter,
            }
        )

    return extra_adapters


@hooks.register('insert_editor_css')
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',  # noqa: P103
        static('cms-admin/css/case-study.css'),
    )


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',  # noqa: P103
        static('cms-admin/css/case-study-index.css'),
    )


@hooks.register('register_bulk_action')
class MigratePage(PageBulkAction):
    display_name = _('Migrate')
    aria_label = _('Create page from page')
    action_type = 'migrate'
    template_name = 'wagtailadmin/microsite_migrate.html'

    # Only gives permission to change pages of the ArticlePage type currently
    def check_perm(self, page):
        return type(page.specific) is ArticlePage

    # TODO update action to create microsite pages from the article pages contained in objects
    # Collect target page from the form in the template and append new pages as the children of that page
    @classmethod
    def execute_action(cls, objects, **kwargs):
        if all(type(object.specific) is ArticlePage for object in objects):
            return len(objects), len([migrate_article_page_to_microsite(object.specific) for object in objects])
        else:
            raise NotImplementedError('execute_action needs to be implemented')


def migrate_article_page_to_microsite(page):
    slug = page.slug
    parent_page = page.get_parent()
    microsite_page = MicrositePage(
        title=page.title,
        page_title=page.article_title,
        page_subheading=page.article_subheading,
        page_teaser=page.article_teaser,
        hero_image=page.article_image,
        page_body=json.dumps(get_microsite_page_body(page.article_body)),
        cta_title=page.cta_title,
        cta_teaser=page.cta_teaser,
        cta_link_label=page.cta_link_label,
        cta_link=page.cta_link,
        related_links=json.dumps(convert_related_links(page)),
        use_domestic_header_logo=True,
    )
    page.delete()
    microsite_page.slug = slug
    parent_page.add_child(instance=microsite_page)


def convert_block_based_on_type(block):
    block_type_conversion_dict = {
        'text': convert_text,
        'cta': convert_cta,
        'Columns': convert_all_columns,
        'Video': convert_video,
        'pull_quote': convert_quote,
        'image': convert_image,
    }

    return block_type_conversion_dict[block.block_type](block)


def get_microsite_page_body(article_page):
    page_body = []
    [page_body.append(convert_block_based_on_type(block)) for block in article_page]
    return page_body


def convert_image(block):
    return {
        'type': 'image',
        'value': block.value.id if block.value else None,
        'id': block.value.file_hash if block.value else None,
    }


def convert_text(block):
    return {'type': 'text', 'value': block.value.source}


def convert_all_columns(block):
    return {
        'type': 'columns',
        'value': [convert_column(value.value) for value in block.value],
    }


def convert_column(block):
    return {
        'type': 'column',
        'value': {
            'text': block.get('description').source,
            'image': block.get('image').id if block.get('image') else None,
            'button_url': block.get('link'),
            'button_label': None,
        },
    }


def convert_cta(block):
    return {
        'type': 'cta',
        'value': {
            'title': block.value.get('title'),
            'teaser': block.value.get('teaser'),
            'link_label': block.value.get('link_label'),
            'link': block.value.get('link'),
        },
    }


def convert_video(block):
    return {
        'type': 'video',
        'value': {'video': block.value.get('video').id if block.value.get('video') else None},
        'id': str(uuid.uuid4()),
    }


def convert_quote(block):
    return {
        'type': 'pull_quote',
        'value': {
            'quote': block.value.get('quote'),
            'role': block.value.get('role'),
            'attribution': block.value.get('attribution'),
            'organisation': block.value.get('organisation'),
            'organisation_link': block.value.get('organisation_link'),
        },
    }


def convert_related_links(page):
    def make_related_link(item):
        return {'type': 'link', 'value': {'title': item['title'], 'full_url': item['link']}, 'id': str(uuid.uuid4())}

    def make_related_page(item):
        {'type': 'page', 'value': item['id'], 'id': str(uuid.uuid4())}

    def get_related_link_conversion(item):
        if item['link'] is not None:
            return make_related_link(item)
        return make_related_page(item)

    related_links = [
        {'id': page.related_page_one_id, 'title': page.related_page_one_title, 'link': page.related_page_one_title},
        {'id': page.related_page_two_id, 'title': page.related_page_two_title, 'link': page.related_page_two_title},
        {
            'id': page.related_page_three_id,
            'title': page.related_page_three_title,
            'link': page.related_page_three_title,
        },
        {'id': page.related_page_four_id, 'title': page.related_page_four_title, 'link': page.related_page_four_title},
        {'id': page.related_page_five_id, 'title': page.related_page_five_title, 'link': page.related_page_five_title},
    ]
    return [get_related_link_conversion(item) for item in related_links if item['id'] is not None or item['link'] != '']


@hooks.register('insert_editor_js')
def toolbar_sticky_by_default():
    return mark_safe(
        """
        <script>
            if (window.localStorage.getItem("wagtail:draftail-toolbar")==null) {
                window.localStorage.setItem("wagtail:draftail-toolbar", "sticky");
            };
        </script>
        """
    )


@hooks.register('register_help_menu_item')
def register_campaign_site_help_menu_item():
    return DismissibleMenuItem(
        _('Campaign Site, getting started'),
        constants.MENU_ITEM_ADD_CAMPAIGN_SITE_LINK,
        icon_name='help',
        order=900,
        attrs={'target': '_blank', 'rel': 'noreferrer'},
        name='campaign-site',
    )


@hooks.register('register_admin_viewset', order=-1)
def register_image_chooser_viewset():
    return AltImageChooserViewSet(
        name='alt_wagtailimages_chooser',
        url_prefix='images/chooser',
    )


@hooks.register('register_icons')
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/video.svg',
        'wagtailfontawesomesvg/solid/download.svg',
        'wagtailfontawesomesvg/solid/heading.svg',
        'wagtailfontawesomesvg/solid/book.svg',
        'wagtailfontawesomesvg/solid/check.svg',
        'wagtailfontawesomesvg/solid/expand.svg',
        'wagtailfontawesomesvg/solid/play.svg',
        'wagtailfontawesomesvg/solid/font.svg',
        'wagtailfontawesomesvg/solid/archive.svg',
        'wagtailfontawesomesvg/solid/question-circle.svg',
        'wagtailfontawesomesvg/solid/quote-left.svg',
        'wagtailfontawesomesvg/solid/calculator.svg',
        'wagtailfontawesomesvg/solid/font.svg',
        'wagtailfontawesomesvg/solid/arrow-right.svg',
        'wagtailfontawesomesvg/solid/comment-dots.svg',
        'anchor-icon/anchor.svg',
    ]


@hooks.register('register_rich_text_features')
def register_rich_text_anchor_identifier_feature(features):
    features.default_features.insert(0, 'anchor-identifier')
    """
    Registering the `anchor-identifier` feature, which uses the `ANCHOR-IDENTIFIER` Draft.js entity type,
    and is stored as HTML with a `<span id="my-anchor" data-id="my-anchor">` tag.
    """
    feature_name = 'anchor-identifier'
    type_ = 'ANCHOR-IDENTIFIER'

    control = {
        'type': type_,
        'label': '',
        'icon': 'anchor',
        'description': 'Anchor Identifier',
    }

    features.register_editor_plugin(
        'draftail',
        feature_name,
        draftail_features.EntityFeature(
            control,
            js=['custom_wagtaildraftailanchors.js'],
        ),
    )

    features.register_converter_rule(
        'contentstate',
        feature_name,
        {
            # Note here that the conversion is more complicated than for blocks and inline styles.
            # 'from_database_format': {'a[data-anchor][id]': AnchorIndentifierEntityElementHandler(type_)},
            'from_database_format': {'a[data-id]': AnchorIndentifierEntityElementHandler(type_)},
            'to_database_format': {'entity_decorators': {type_: anchor_identifier_entity_decorator}},
        },
    )

    features.register_link_type(AnchorIdentifierLinkHandler)


@hooks.register('register_rich_text_features')
def register_strong_feature(features):
    """
    Registering the `strong` feature. It will render bold text with `strong` tag.
    Default Wagtail uses the `b` tag.
    """
    feature_name = 'strong'
    type_ = 'BOLD'
    tag = 'strong'

    control = {
        'type': type_,
        'icon': 'bold',
        'description': 'Bold',
    }

    features.register_editor_plugin('draftail', feature_name, draftail_features.InlineStyleFeature(control))

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_em_feature(features):
    """
    Registering the `em` feature. It will render italic text with `em` tag.
    Default Wagtail uses the `i` tag for italics.
    """
    feature_name = 'em'
    type_ = 'ITALIC'
    tag = 'em'

    control = {
        'type': type_,
        'icon': 'italic',
        'description': 'Italic',
    }

    features.register_editor_plugin('draftail', feature_name, draftail_features.InlineStyleFeature(control))

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)


# Update expiry date for campaign and microsite pages using MicrositePage expiry_date field, which defaults to one year.
@hooks.register('after_publish_page')
def set_microsite_expiry_date(request, page):
    page_template_names = ['microsites/micro_site_page.html']

    # Checks if the page type is in the list and whether the expiry date has been changed since last publish
    if page.template in page_template_names and page.expire_at != page.expiry_date:
        page.expire_at = page.expiry_date
        page.save_revision()


@hooks.register('after_edit_page')
def after_edit_page(request, page):
    if isinstance(page, CountryGuidePage):
        if request.method == 'POST':
            messages.add_message(
                request,
                messages.ERROR,
                'Please note though that economic growth and GDP per capita data is provided by the '
                'IMF API and cannot be edited.',
            )


class SectorTagsSnippetViewSet(ModelViewSet):
    form_fields = ['name', 'slug']
    model = SectorTag
    icon = 'tag'  # change as required
    menu_label = 'Sector Tags'
    menu_order = 400  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ['name', 'slug']
    search_fields = ('name',)


class CountryTagsSnippetViewSet(ModelViewSet):
    form_fields = ['name']  # only show the name field
    model = CountryTag
    icon = 'tag'  # change as required
    menu_label = 'Country Tags'
    menu_order = 400  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ['name', 'slug']
    search_fields = ('name',)


class TypeOfExportTagsSnippetViewSet(ModelViewSet):
    form_fields = ['name']  # only show the name field
    model = TypeOfExportTag
    icon = 'tag'  # change as required
    menu_label = 'Type of Export Tags'
    menu_order = 400  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ['name', 'slug']
    search_fields = ('name',)


class RegionTagsSnippetViewSet(ModelViewSet):
    form_fields = ['name']  # only show the name field
    model = PersonalisationRegionTag
    icon = 'tag'  # change as required
    menu_label = 'Region Tags'
    menu_order = 400  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ['name', 'slug']
    search_fields = ('name',)


class TradingBlocTagsSnippetViewSet(ModelViewSet):
    form_fields = ['name']  # only show the name field
    model = PersonalisationTradingBlocTag
    icon = 'tag'  # change as required
    menu_label = 'Trading Bloc Tags'
    menu_order = 400  # will put in 3rd place (000 being 1st, 100 2nd)
    list_display = ['name', 'slug']
    search_fields = ('name',)


class TagsViewSetGroup(ModelViewSetGroup):
    items = (
        SectorTagsSnippetViewSet,
        CountryTagsSnippetViewSet,
        TypeOfExportTagsSnippetViewSet,
        RegionTagsSnippetViewSet,
        TradingBlocTagsSnippetViewSet,
    )
    add_to_admin_menu = True
    menu_label = 'Tags'
    menu_icon = 'tag'
    menu_order = 400


register_snippet(TagsViewSetGroup)


@hooks.register('construct_main_menu')
def hide_tagging_menu_item(request, menu_items):
    if not request.user.groups.filter(name='Tagging').exists():
        menu_items[:] = [item for item in menu_items if item.label != 'Tags']


@hooks.register('is_response_cacheable')
def nocache_certain_response_status_codes(response, curr_cache_decision):
    if response.status_code in (
        302,
        301,
        403,
    ):
        return False
