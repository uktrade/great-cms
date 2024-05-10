web: ./scripts/entry.sh
celery_worker: celery -A config worker -l DEBUG
celery_beat: celery -A config beat -l info -S django
