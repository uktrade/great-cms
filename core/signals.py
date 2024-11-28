from django.db.models.signals import pre_save
from django.dispatch import receiver
from wagtail.documents.models import Document

from core.tasks import handle_file_upload


@receiver(pre_save, sender=Document)
def document_pre_save_handler(sender, instance, **kwargs):
    print("Signals")
    if instance.file:
        file_path = instance.file.name
        handle_file_upload.delay(file_path, instance.title, instance.collection_id)
