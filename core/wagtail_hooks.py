from great_components.helpers import add_next
from wagtail.core import hooks

from django.urls import reverse
from django.shortcuts import redirect

from core import mixins, views

from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from datetime import timedelta
import readtime

from core import models

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


@hooks.register('after_edit_page')
def set_read_time(request, page):
    if hasattr(page, 'estimated_read_duration'):
        html = render_to_string(page.template, {'page': page, 'request': request})
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.body.find_all(['script', 'noscript', 'link', 'style', 'meta']):
            tag.decompose()
        seconds = readtime.of_html(str(soup.body)).seconds
        page.estimated_read_duration = timedelta(seconds=seconds)
        page.save_revision()
        return seconds


@hooks.register('after_edit_page')
def set_lesson_pages_topic_id(request, page):
    if hasattr(page, 'topics'):
        topic_map = {}
        # build a map of all the topics-lessons for this curated page
        for topic in page.topics:
            topic_map[topic.id] = []
            for lesson_page in topic.value['pages']:
                topic_map[topic.id].append(lesson_page.id)

        for topic_id, lesson_ids in topic_map.items():
            # Set the topic to any lesson which don't have this topic set
            lesson_to_update = models.DetailPage.objects.filter(id__in=lesson_ids).exclude(topic_block_id=topic_id)
            for lesson in lesson_to_update:
                lesson.topic_block_id = topic_id
                lesson.save()
            # Blank the topic to any lessons which have lesson set which aren't in the map
            lesson_to_blank = models.DetailPage.objects.filter(topic_block_id=topic_id).exclude(id__in=lesson_ids)
            for lesson in lesson_to_blank:
                lesson.topic_block_id = None
                lesson.save()
    return page
