from importlib import import_module, reload
import sys

import requests

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.urls import clear_url_caches

from wagtail.core.models import Collection
from wagtailmedia import models as wagtailmedia_models


def create_response(json_body={}, status_code=200, content=None):
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_body
    response._content = content
    return response


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)



def make_test_video(
    content=b'An example movie file',
    filename='movie.mp4',
    duration=120,
    transcript=None,
    collection_name='Root'
):

    fake_file = ContentFile(content)
    fake_file.name = filename
    root_collection = Collection.objects.create(name=collection_name, depth=0)
    media_model = wagtailmedia_models.get_media_model()
    media = media_model(collection=root_collection)

    media.file = File(fake_file)
    media.transcript = transcript

    return media
