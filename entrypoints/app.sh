#!/bin/sh

python manage.py migrate --noinput

if [[ "$COPILOT_ENVIRONMENT_NAME" == "dev" ]]; then
   echo "Dev Environment Detected"
   echo "$COPILOT_ENVIRONMENT_NAME"
   ddtrace-run gunicorn config.wsgi --bind 0.0.0.0:$PORT
else
   echo "Dev Environment Not Detected"
   echo "$COPILOT_ENVIRONMENT_NAME"
   gunicorn config.wsgi --bind 0.0.0.0:$PORT
fi
