from django import template
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

from core.constants import VIDEO_DURATION_DATA_ATTR_NAME

register = template.Library()


def _get_poster_attribute(video):
    if video and video.thumbnail:
        return f'poster="{video.thumbnail.url}" '  # trailing space is deliberate
    return ''


@register.simple_tag
def render_video(block):
    """Renders a video block (eg in a lesson hero or a case study).

    Includes a custom attribute on the video element so we can estimate
    page view time in our post-save hook, without clashing with the automatically
    added `duration` attribute that a browser may add to <video>.
    """

    if not block:
        return ''

    video_duration = getattr(block['video'], 'duration', 0)
    # The default, above, _should_ never be needed because field is mandatory in the CMS

    video = block['video']

    timestamp_to_allow_poster_image_to_work_on_mobile_safari = '#t=0.1'

    sources_data = []
    for source in video.sources:
        if 'src' in source:
            source['src'] += timestamp_to_allow_poster_image_to_work_on_mobile_safari
        sources_data.append([flatatt(source)])

    sources = format_html_join('\n', '<source{0}>', sources_data)

    return format_html(
        f"""
            <video preload="metadata" controls
            {_get_poster_attribute(video)}{VIDEO_DURATION_DATA_ATTR_NAME}="{video_duration}">
                {sources}
                Your browser does not support the video tag.
            </video>
            <div class="video-transcript-container"></div>
        """
    )
