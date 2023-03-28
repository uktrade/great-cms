from io import BytesIO

from celery.utils.log import get_task_logger

from config.celery import app

logger = get_task_logger(__name__)


@app.task
def upload_media(model, content):
    try:
        logger.info(f"CoreTask: starting {model} ,content {len(content)}")
        file_to_upload = BytesIO(content)

        logger.info("CoreTask: bytes loaded")
        model.file.save(model.file.name, file_to_upload, save=False)
        logger.info("CoreTask: finished s3 upload")
        # Rename title as completed
        # model_instance = models.GreatMedia.objects.get(file=file_name)
        # model_instance.title = model.title
        # model_instance.save()
        # logger.info("CoreTask: model updated")
    except Exception as e:
        logger.error(f'CoreTask: Task failed {str(e)}')
