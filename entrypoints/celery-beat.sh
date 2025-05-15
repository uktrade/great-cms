#!/bin/bash

if [[ "$FEATURE_DATADOG" = true ]]; then
   ddtrace-run celery -A config beat -l info -S django
else
   gunicorn celery -A config beat -l info -S django
fi
