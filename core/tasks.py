import os

from celery.utils.log import get_task_logger

from config.celery import app

log = get_task_logger(__name__)


@app.task
def upload_media(file, file_name):
    log.info(f'hello {file} ,path {file_name}')
    with open(file_name, 'rb') as f:
        file.save(file.name, f, save=False)

    # Delete temp file after uploading
    os.remove(file_name)

    # TODO send email, update wagtail media model
