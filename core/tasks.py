import os

from celery.utils.log import get_task_logger

from config.celery import app
from core import models

logger = get_task_logger(__name__)


@app.task
def upload_media(model, file_name):
    try:
        logger.info(f"CoreTask: starting {model} ,path {file_name}")

        with open(file_name, 'rb') as f:
            logger.info("CoreTask: file opened")
            model.file.save(model.file.name, f, save=False)

        logger.info("CoreTask: finished s3 upload")
        # Delete temp file after uploading
        os.remove(file_name)
        # Rename title as completed
        model_instance = models.GreatMedia.objects.get(file=file_name)
        model_instance.title = model.title
        model_instance.save()
        logger.info("CoreTask: model updated")
    except Exception as e:
        logger.error(f'CoreTask: Task failed {str(e)}')
