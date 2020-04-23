from django import template
from django.forms.utils import flatatt
from django.utils.html import format_html_join, format_html

register = template.Library()


@register.simple_tag
def render_video_block(value):
    if not value:
        return ''
    sources = format_html_join('\n', '<source{0}>', [[flatatt(source)] for source in value['video'].sources])
    return format_html(
        f"""
                <div>
                    <video width="{value['width']}" height="{value['height']}" controls>
                        {sources}
                        Your browser does not support the video tag.
                    </video>
                </div>
                """
    )
