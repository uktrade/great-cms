#!/bin/sh

python manage.py migrate --noinput && ddtrace-run gunicorn config.wsgi --bind 0.0.0.0:$PORT

#if [[ "$COPILOT_ENVIRONMENT_NAME" == "dev" ]]; then
#   ddtrace-run gunicorn config.wsgi --bind 0.0.0.0:$PORT
#else
#   gunicorn config.wsgi --bind 0.0.0.0:$PORT
#fi
