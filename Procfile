web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn --timeout 300 config.wsgi --graceful-timeout=120 --workers 4 --worker-class=gevent --bind 0.0.0.0:$PORT
celery_worker: celery -A config worker -l DEBUG
celery_beat: celery -A config beat -l info -S django
