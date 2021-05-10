from io import BytesIO

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def format_two_dp(num):
    return '{0:.2f}'.format(num)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pisa_status = pisa.pisaDocument(BytesIO(html.encode('utf8')), result)
    pdf_file = ContentFile(result.getvalue())
    if not pisa_status.err:
        return (HttpResponse(result.getvalue(), content_type='application/pdf'), pdf_file)
    return None, None
