import readtime
import readtime.result

from django import template
from django.template.loader import render_to_string
from django.utils.translation.trans_null import ngettext


register = template.Library()


class Result(readtime.result.Result):

    @property
    def hours(self):
        hours = int(round(self.minutes / 60))
        if hours < 1:
            hours = 1
        return hours

    @property
    def text(self):
        if self.minutes < 60:
            suffix = ngettext(singular='min', plural='mins', number=self.minutes)
            number = self.minutes
        else:
            suffix = ngettext(singular='hour', plural='hours', number=self.hours)
            number = self.hours
        return f'{number} {suffix}'


@register.simple_tag(takes_context=True)
def read_time(context, pages):
    seconds = []
    for page in pages:
        page = page.specific
        html = render_to_string(page.template, page.get_context(context['request']))
        seconds.append(readtime.of_html(html).seconds)
    result = Result(seconds=sum(seconds))
    return result.text
