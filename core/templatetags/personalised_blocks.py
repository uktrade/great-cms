from django import template
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join

register = template.Library()


def _get_poster_attribute(video):
    if video and video.thumbnail:
        return f'poster="{video.thumbnail.url}" '  # Trailing final space is deliberate
    return ''


@register.simple_tag
def render_video_block(block):
    """Renders a video specifically added via a PersonalisedStructBlock

    Note that the viewing time is NOT added to the <video> node as a custom
    attribute, unlike what happens in video_tags.render_video(). This is
    because we don't count viewing time of personalised content in estimated
    reads, so there's no need for it.
    """

    if not block:
        return ''
    video = block['video']
    sources = format_html_join('\n', '<source{0}>', [[flatatt(source)] for source in video.sources])
    return format_html(
        f"""
                <div>
                    <video {_get_poster_attribute(video)}width="{block['width']}" height="{block['height']}" controls>
                        {sources}
                        Your browser does not support the video tag.
                    </video>
                </div>
                """
    )
