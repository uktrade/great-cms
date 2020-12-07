import datetime
import json
import logging
import readtime

from urllib.parse import urlparse

import boto3
from bs4 import BeautifulSoup
from great_components.helpers import add_next

from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models as django_models
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse

from wagtail.core import hooks
from wagtail.core.models import Page
from wagtail_transfer.files import File as WTFile, FileTransferError
from wagtail_transfer.field_adapters import FieldAdapter
from wagtail_transfer.models import ImportedFile

from core import constants, mixins, views

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
            return redirect(page.authenticated_user_required_redirect_url)


@hooks.register('before_serve_page')
def login_required_signup_wizard(page, request, serve_args, serve_kwargs):
    if page.template == 'learn/detail_page.html' and request.user.is_anonymous:

        # opting out of personalised content 'forever' - not just this request.
        if 'show-generic-content' in request.GET:
            request.session[SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT] = True

        if not request.session.get(SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT):
            signup_url = reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START})
            url = add_next(destination_url=signup_url, current_url=request.get_full_path())
            return redirect(url)


def _update_data_for_appropriate_version(
    page: Page,
    force_page_update: bool,
    data_to_update: dict
) -> None:
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
    latest_revision_json = json.loads(latest_revision.content_json)

    for key, value in data_to_update.items():
        # We need to watch out for the timedelta, because it serialises to
        # a different format (PxDTxxHxxMxxS) by default
        if isinstance(value, datetime.timedelta):
            value = str(value)
        latest_revision_json[key] = value

    latest_revision.content_json = json.dumps(latest_revision_json, cls=DjangoJSONEncoder)
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
        video_nodes = soup.find_all(
            'video', attrs={
                constants.VIDEO_DURATION_DATA_ATTR_NAME: True
            }
        )
        watching_seconds = sum([
            int(node.get(constants.VIDEO_DURATION_DATA_ATTR_NAME, 0)) for node in video_nodes
        ])
        seconds = reading_seconds + watching_seconds

        _update_data_for_appropriate_version(
            page=page,
            force_page_update=is_post_creation,
            data_to_update={'estimated_read_duration': datetime.timedelta(seconds=seconds)}
        )


class S3WagtailTransferFile(WTFile):
    """Subclass of File that knows how to transfer() using an
    S3 to S3 copy"""

    def __init__(self, local_filename, size, hash_, source_url, **kwargs):
        super().__init__(
            local_filename=local_filename,
            size=size,
            hash=hash_,
            source_url=source_url
        )

        self.source_bucket = kwargs['source_bucket']
        self.source_key = kwargs['source_key']

    def transfer(self):

        # NB: This will only work if the source file is publicly readable
        copy_source = {
            'Bucket': self.source_bucket,
            'Key': self.source_key
        }

        try:
            s3.meta.client.copy(
                copy_source,
                settings.AWS_STORAGE_BUCKET_NAME,
                self.local_filename
            )
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
        return {
            'size': _object_summary.size,
            'hash': self._get_file_hash(_object_summary)
        }

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
            source_bucket, source_key = self._get_imported_file_bucket_and_key(
                source_file_url
            )

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
        extra_adapters.update({
            django_models.FileField: S3FileFieldAdapter,
        })

    return extra_adapters
