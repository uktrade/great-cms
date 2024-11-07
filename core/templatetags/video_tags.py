from django import template
from django.forms.utils import flatatt
from django.template.defaultfilters import linebreaksbr
from django.template.loader import render_to_string
from django.utils.html import format_html, format_html_join

from core.constants import VIDEO_DURATION_DATA_ATTR_NAME

register = template.Library()


def _get_poster_attribute(video):
    if video and video.thumbnail:
        return f'poster="{video.thumbnail.url}" '  # trailing space is deliberate
    return ''


@register.simple_tag
def render_video(block, event_name=None):  # noqa: C901
    """Renders a video block (eg in a lesson hero or a case study).

    Includes a custom attribute on the video element so we can estimate
    page view time in our post-save hook, without clashing with the automatically
    added `duration` attribute that a browser may add to <video>.
    """

    if not block:
        return ''

    video_duration = getattr(block['video'], 'duration', 0)
    # The default, above, _should_ never be needed because field is mandatory in the CMS
    video_transcript = getattr(block['video'], 'transcript', '')

    video = block['video']
    video_title = video.title
    timestamp_to_allow_poster_image_to_work_on_mobile_safari = '#t=0.1'

    sources_data = []
    for source in video.sources:
        if 'src' in source:
            source['src'] += timestamp_to_allow_poster_image_to_work_on_mobile_safari
        sources_data.append([flatatt(source)])

    sources = format_html_join('\n', '<source{0}>', sources_data)

    if video.subtitles:
        rendered_subtitles = []
        for subtitle_spec in video.subtitles:
            rendered_subtitles.append(
                render_to_string(
                    'core/includes/_video_subtitle.html',
                    subtitle_spec,
                )
            )
        subtitles = '\n'.join(rendered_subtitles)

    else:
        subtitles = ''

    transcript_container = ''

    hidden_text = event_name if event_name else video.title

    if video_transcript:

        min_length = 1000
        end_position = video_transcript.find('.', min_length)

        if end_position != -1:
            initial_transcript = video_transcript[: end_position + 1]
        else:
            initial_transcript = video_transcript[:min_length]

        show_full_transcript_details = len(initial_transcript) < len(video_transcript)

        transcript_container = """<details
            class="govuk-details govuk-!-static-padding-top-4 govuk-!-static-margin-bottom-0"
            data-module="govuk-details">
                <summary class="govuk-details__summary">
                    <span class="govuk-details__summary-text">"""
        if hidden_text:
            transcript_container = f"""{transcript_container}<span class="govuk-visually-hidden">
                View transcript for {hidden_text} recording</span>
                <span aria-hidden="true">View transcript</span>"""
        else:
            transcript_container = f"""{transcript_container}View Transcript"""

        transcript_container = f"""{transcript_container}</span>
                </summary>
                <div class="govuk-details__text govuk-body great-video-transcipt-text govuk-!-margin-0">
                    {linebreaksbr(initial_transcript)}
                    {'<div class="govuk-!-margin-top-2">'
                     '<a class="govuk-link" href="?fullTranscript=true">'
                     'Read full transcript'
                     '</a>'
                     '</div>' if show_full_transcript_details else ''}
                </div>
            </details>
        """

    rendered = format_html(
        f"""
            <video preload="metadata" controls controlsList="nodownload"
            {_get_poster_attribute(video)}
            data-title="{video_title}"
            {VIDEO_DURATION_DATA_ATTR_NAME}="{video_duration}">
                {sources}
                {subtitles}
                Your browser does not support the video tag.
            </video>
            {transcript_container}
        """
    )

    return rendered


@register.simple_tag
def get_video_transcript(block):
    video_transcript = getattr(block['video'], 'transcript', '')
    rendered = format_html(
        f"""
            {linebreaksbr(video_transcript)}
        """
    )

    return rendered
