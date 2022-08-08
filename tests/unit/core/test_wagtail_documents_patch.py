from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from wagtail.core.models import Collection
from wagtail.documents import models

from tests.helpers import create_response


@pytest.fixture
def wagtail_document():
    collection, _ = Collection.objects.get_or_create(name='Root', depth=0)
    document = models.Document.objects.create(title='Test document', collection=collection)

    yield document

    models.Document.objects.all().delete()
    Collection.objects.all().delete()


@pytest.mark.django_db
@override_settings(WAGTAILDOCS_EXTENSIONS=['txt'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['text/plain'])
def test_wagtail_document_validation_extension_valid(wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'file_content', content_type='text/plain')
    wagtail_document.file = file

    try:
        wagtail_document.clean()
    except ValidationError:
        pytest.fail('Should not raise a validator error.')


@pytest.mark.django_db
@override_settings(WAGTAILDOCS_EXTENSIONS=['pdf'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['application/pdf'])
def test_wagtail_document_validation_extension_invalid(wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'file_content', content_type='application/pdf')
    wagtail_document.file = file

    with pytest.raises(ValidationError) as exception:
        wagtail_document.clean()

    assert "File extension 'txt' is not allowed. Allowed extensions are: 'pdf'." in exception.value


@pytest.mark.django_db
@override_settings(WAGTAILDOCS_EXTENSIONS=['txt'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['text/plain'])
def test_wagtail_document_validation_mime_type_valid(wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'file_content', content_type='text/plain')
    wagtail_document.file = file

    try:
        wagtail_document.clean()
    except ValidationError:
        pytest.fail('Should not raise a validator error.')


@pytest.mark.django_db
@override_settings(WAGTAILDOCS_EXTENSIONS=['txt'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['application/pdf'])
def test_wagtail_document_validation_mime_type_invalid(wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'A boring example document', content_type='text/plain')
    wagtail_document.file = file

    with pytest.raises(ValidationError) as exception:
        wagtail_document.clean()

    assert "File's mime type not allowed." in exception.value


@pytest.mark.django_db
@override_settings(CLAM_AV_ENABLED=True)
@override_settings(WAGTAILDOCS_EXTENSIONS=['txt'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['text/plain'])
@mock.patch('core.helpers.ClamAvClient.scan_chunked')
def test_wagtail_document_validation_scan_valid(mock_clam_av_client_scan, wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'A boring example document', content_type='text/plain')

    mock_response = create_response({'malware': False, 'reason': None, 'time': 0.011951766995480284})
    mock_clam_av_client_scan.return_value = mock_response

    wagtail_document.file = file

    try:
        wagtail_document.clean()
    except ValidationError:
        pytest.fail('Should not raise a validator error.')


@pytest.mark.django_db
@override_settings(CLAM_AV_ENABLED=True)
@override_settings(WAGTAILDOCS_EXTENSIONS=['txt'])
@override_settings(WAGTAILDOCS_MIME_TYPES=['text/plain'])
@mock.patch('core.helpers.ClamAvClient.scan_chunked')
def test_wagtail_document_validation_scan_invalid(mock_clam_av_client_scan, wagtail_document):
    file = SimpleUploadedFile('file.txt', content=b'A boring example document', content_type='text/plain')

    mock_response = create_response({'malware': True, 'reason': 'Win.Test.EICAR_HDB-1', 'time': 0.005419833003543317})
    mock_clam_av_client_scan.return_value = mock_response

    wagtail_document.file = file

    with pytest.raises(ValidationError) as exception:
        wagtail_document.clean()

    assert 'Rejected: uploaded file did not pass security scan' in exception.value
