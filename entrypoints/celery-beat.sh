#!/bin/bash

if [[ "$COPILOT_ENVIRONMENT_NAME" == "dev" ]]; then
   ddtrace-run celery -A config beat -l info -S django
else
   gunicorn celery -A config beat -l info -S django
fi
