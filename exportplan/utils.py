from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def format_two_dp(num):
    return '{0:.2f}'.format(num)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf8')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
