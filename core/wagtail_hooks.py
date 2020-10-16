import datetime
import json

from datetime import timedelta

from bs4 import BeautifulSoup
import readtime

from great_components.helpers import add_next
from wagtail.core import hooks
from wagtail.core.models import Page

from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect
from django.template.loader import render_to_string

from core import constants, mixins, views, models

SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT = 'LESSON_PAGE_SHOW_GENERIC_CONTENT'
exportplan_templates = ['exportplan/automated_list_page.html', 'exportplan/dashboard_page.html']


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

        # opting out of personalised content "forever" - not just this request.
        if 'show-generic-content' in request.GET:
            request.session[SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT] = True

        if not request.session.get(SESSION_KEY_LESSON_PAGE_SHOW_GENERIC_CONTENT):
            signup_url = reverse('core:signup-wizard-tailored-content', kwargs={'step': views.STEP_START})
            url = add_next(destination_url=signup_url, current_url=request.get_full_path())
            return redirect(url)

    elif page.template in exportplan_templates and request.user.is_anonymous:
        signup_url = reverse('core:signup-wizard-export-plan', kwargs={'step': views.STEP_START})
        url = add_next(destination_url=signup_url, current_url=request.get_full_path())
        return redirect(url)


def _update_data_for_appropriate_version(page: Page, data_to_update: dict) -> None:
    """For a given Page instance, use the provided data to update either:
        * its latest revision ONLY, if there are unpublished changes (ie, its a Draft)
        or
        * the latest revision AND the live page, if the revision is the one that became
        the live page. (We update the revision for consistency and history.)
    """

    latest_revision = page.get_latest_revision()
    latest_revision_json = json.loads(latest_revision.content_json)

    # 1. Update the revision, whether it's for the latest Draft or the
    # revision which created the current Live page
    for key, value in data_to_update.items():
        # We need to watch out for the timedelta, because it serialises to
        # a different format (PxDTxxHxxMxxS) by default
        if isinstance(value, datetime.timedelta):
            value = str(value)
        latest_revision_json[key] = value

    latest_revision.content_json = json.dumps(latest_revision_json, cls=DjangoJSONEncoder)
    latest_revision.save()

    if not page.has_unpublished_changes:
        # 2. The live version is based on the latest revision, which means
        # we also need to update the live page, because it won't automatically
        # reflect the chages we made to that revision.

        # This update()-based approach is awkward but we want to update the
        # Page record without any side effects via save() etc
        queryset_for_page = type(page).objects.filter(id=page.id)
        queryset_for_page.update(**data_to_update)


@hooks.register('after_edit_page')
def set_read_time(request, page):
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
            data_to_update={'estimated_read_duration': timedelta(seconds=seconds)}
        )


@hooks.register('after_edit_page')
def set_lesson_pages_topic_id(request, page):
    if hasattr(page, 'topics'):
        topic_map = {}
        # build a map of all the topics->lessons for this curated page
        for topic in page.topics:
            topic_map[topic.id] = []
            for item in topic.value['lessons_and_placeholders']:
                if item.block_type == constants.LESSON_BLOCK:
                    lesson_page = item.value
                    topic_map[topic.id].append(lesson_page.id)

        for topic_id, lesson_ids in topic_map.items():
            # Set the topic to any lesson which don't have this topic set
            lesson_to_update = models.DetailPage.objects.filter(
                id__in=lesson_ids
            ).exclude(
                topic_block_id=topic_id
            )
            for lesson in lesson_to_update:
                lesson.topic_block_id = topic_id
                lesson.save()

            # Blank the topic to any lessons which have lesson set which aren't in the map
            lesson_to_blank = models.DetailPage.objects.filter(
                topic_block_id=topic_id
            ).exclude(
                id__in=lesson_ids
            )
            for lesson in lesson_to_blank:
                lesson.topic_block_id = None
                lesson.save()
    return page
