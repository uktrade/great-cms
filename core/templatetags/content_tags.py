import readtime
import readtime.result

from django import template
from django.template.loader import render_to_string
from django.utils.translation.trans_null import ngettext


register = template.Library()


class Result(readtime.result.Result):

    @property
    def minutes_suffix(self):
        return ngettext(singular='min', plural='mins', number=self.minutes)

    @property
    def text(self):
        if self.minutes < 60:
            return f'{self.minutes} {self.minutes_suffix}'
        else:
            hours, minutes = divmod(self.minutes, 60)
            suffix = ngettext(singular='hour', plural='hours', number=hours)
            if minutes:
                return f'{hours} {suffix} {minutes} {self.minutes_suffix}'
            return f'{hours} {suffix}'


@register.simple_tag(takes_context=True)
def read_time(context, pages):
    seconds = []
    for page in pages:
        page = page.specific
        html = render_to_string(page.template, page.get_context(context['request']))
        seconds.append(readtime.of_html(html).seconds)
    result = Result(seconds=sum(seconds))
    return result.text
