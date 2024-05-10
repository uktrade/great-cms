python manage.py collectstatic --noinput
python manage.py migrate --noinput
if [ -n "${COPILOT_ENVIRONMENT_NAME}" ]; then
    echo "Running in DBT Platform"
    opentelemetry-instrument gunicorn config.wsgi --bind 0.0.0.0:$PORT
else
    gunicorn config.wsgi --bind 0.0.0.0:$PORT
fi
