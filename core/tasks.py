import os

from celery.utils.log import get_task_logger

from config.celery import app
from core import models

log = get_task_logger(__name__)


@app.task
def upload_media(model, file_name):
    log.info(f'hello {model} ,path {file_name}')
    with open(file_name, 'rb') as f:
        model.file.save(model.file.name, f, save=False)

    # Delete temp file after uploading
    os.remove(file_name)

    # Rename title as completed
    model_instance = models.GreatMedia.objects.get(file=file_name)
    model_instance.title = model.title
    model_instance.save()
