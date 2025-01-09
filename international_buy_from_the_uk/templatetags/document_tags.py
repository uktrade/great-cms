from django import template
from wagtail.documents.models import Document

register = template.Library()


@register.simple_tag
def get_document_link(document_title: str, document_type) -> str:
    try:
        document = Document.objects.get(title=document_title)
    except Document.DoesNotExist:
        return ''
    else:
        return f'/documents/{document.id}/{document_title}.{document_type}'
