web: python manage.py collectstatic --noinput && python manage.py distributed_migrate --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
