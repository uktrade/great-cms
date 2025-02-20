web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && ddtrace-run gunicorn config.wsgi --bind 0.0.0.0:$PORT
app: ./entrypoints/app.sh
celery_worker: ./entrypoints/celery-worker.sh
celery_beat: ./entrypoints/celery-beat.sh
