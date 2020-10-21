import json
from importlib import import_module, reload
import sys

import requests

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.urls import clear_url_caches

from wagtail.core.models import Collection
from wagtailmedia import models as wagtailmedia_models

from core.models import CuratedListPage


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
    title='Test file',
    content=b'An example movie file',
    filename='movie.mp4',
    duration=120,
    transcript=None,
    collection_name='Root'
):
    fake_file = ContentFile(content)
    fake_file.name = filename
    root_collection, _ = Collection.objects.get_or_create(
        name=collection_name,
        depth=0
    )
    media_model = wagtailmedia_models.get_media_model()
    media = media_model(collection=root_collection)
    media.title = title
    media.file = File(fake_file)
    media.duration = duration
    media.transcript = transcript

    return media


def add_lessons_and_placeholders_to_curated_list_page(
    curated_list_page: CuratedListPage,
    data_for_topics: dict,
) -> CuratedListPage:

    """Because it's very, very fiddly to set up the factories to populate the
    `lessons_and_placeholders` StreamBlock with our current modelling, this
    helper sets them via JSON _and republishes the Page_.

    args:
        clp: CuratedListPage instance
        data_for_topics: dict with

            - keys, to be used as indices (ie, array indices for each each block in `topics`)

            - VERY SPECIFIC values (ie, the data structure of data_for_topics doesn't map
            to the streamfield data, it's about making the data setup easier for tests):

                - id: the id for the TOPIC block, optional
                - title: the title for the TOPIC block, optional, nested below topic['value']
                - lessons_and_placeholders: these will be nested below topic['value']

            eg

            {
                0: {
                    'id': 'optional string id for the TOPIC here',
                    'title': 'optional string title for the TOPIC here',
                    'lessons_and_placeholders': [
                        {'type': 'lesson', 'value': detail_page_1.id},
                        {'type': 'lesson', 'value': detail_page_2.id},
                        {'type': 'placeholder', 'value': {'title': 'Placeholder One'}},
                    ]
                },
                1: {
                    'id': "optional string id for the TOPIC here",
                    'title': 'optional string title for the TOPIC here',
                    'lessons_and_placeholders': [
                        {'type': 'lesson', 'value': detail_page_3.id},
                    ],
                },
                ...
            }
    """

    page_json = json.loads(curated_list_page.to_json())
    page_topics_json = json.loads(page_json['topics'])

    for idx, data in data_for_topics.items():
        try:
            page_topics_json[idx]
        except IndexError:
            # No topic data bootstrapped, so need to lay in the basic structure
            # of a topic block's data
            page_topics_json.append(
                {
                    'type': 'topic',
                    'value': {}
                }
            )

        page_topics_json[idx]['value']['lessons_and_placeholders'] = (
            data['lessons_and_placeholders']
        )
        if data.get('title'):
            page_topics_json[idx]['value']['title'] = data['title']
        if data.get('id'):
            page_topics_json[idx]['id'] = data['id']

    page_json['topics'] = json.dumps(page_topics_json)
    new_revision = curated_list_page.revisions.create(
        content_json=json.dumps(page_json)
    )
    new_revision.publish()
    curated_list_page.refresh_from_db()

    return curated_list_page
