from celery.utils.log import get_task_logger

from config.celery import app

log = get_task_logger(__name__)


@app.task
def upload_media(model, file_path):
    log.info('hello %s', model)
    model.file.save(model.file.name, open(file_path, 'rb'), save=False)
