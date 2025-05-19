#!/bin/bash

if [[ "$FEATURE_DATADOG" = true ]]; then
   ddtrace-run celery -A config beat -l info -S django
else
   celery -A config beat -l info -S django
fi
