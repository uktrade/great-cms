web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT 
app: python manage.py migrate --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
celery_worker: celery -A config worker -l DEBUG
celery_beat: celery -A config beat -l info -S django
