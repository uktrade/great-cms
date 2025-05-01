from django.core.exceptions import FieldError
from django.db.models.signals import post_delete, post_save
from wagtail.search import index
from wagtail.search.signal_handlers import post_delete_signal_handler
from wagtail.search.tasks import insert_or_update_object_task


def post_save_signal_handler(instance, **kwargs):
    """
    We only want to update_or_create the index if both nofollow and noindex are true
    """
    try:
        instance = None if instance.meta_robots_nofollow or instance.meta_robots_noindex else instance
    except FieldError:
        pass
    if instance:
        insert_or_update_object_task.enqueue(instance._meta.app_label, instance._meta.model_name, str(instance.pk))


def register_signal_handlers():
    # Loop through list and register signal handlers for each one
    for model in index.get_indexed_models():
        post_save.connect(post_save_signal_handler, sender=model)
        post_delete.connect(post_delete_signal_handler, sender=model)
