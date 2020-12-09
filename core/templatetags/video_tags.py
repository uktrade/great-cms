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

    This attribute is NOT present on a video used in a PersonalisedStructBlock – see
    personalised_blocks.render_video_block()
    """

    if not block:
        return ''

    video_duration = getattr(block['video'], 'duration', 0)
    # The default, above, _should_ never be needed because field is mandatory in the CMS

    video = block['video']

    sources = format_html_join('\n', '<source{0}>', [[flatatt(source)] for source in video.sources])

    return format_html(
        f"""
            <video controls {_get_poster_attribute(video)}{VIDEO_DURATION_DATA_ATTR_NAME}="{video_duration}">
                {sources}
                Your browser does not support the video tag.
            </video>
            <div class="video-transcript-container"></div>
        """
    )
