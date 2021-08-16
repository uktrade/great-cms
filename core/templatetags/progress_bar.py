from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def progress_bar(total, complete):
    """
    Renders a progress bar given total and completed
    """
    if total == '':
        total = 0

    percentage = int((complete / total) * 100) if (total or 0) > 0 else 0

    return format_html(
        f"""
            <div class="progress-bar">
                <span style="width:{percentage}%"></span>
            </div>
        """
    )
