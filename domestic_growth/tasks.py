from django.core.management import call_command

from config.celery import app


@app.task
def move_incomplete_triage_data_from_cache_to_db():
    call_command('move_triage_data_from_cache_to_db')
