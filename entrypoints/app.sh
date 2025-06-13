#!/bin/bash

python manage.py migrate --noinput

if [[ "$FEATURE_DATADOG" = true ]]; then
   echo "Datadog Detected"
   echo "$COPILOT_ENVIRONMENT_NAME"
   ddtrace-run gunicorn config.wsgi --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker
else
   echo "Datadog Not Detected"
   echo "$COPILOT_ENVIRONMENT_NAME"
   gunicorn config.wsgi --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker
fi
