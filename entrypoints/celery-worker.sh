#!/bin/sh

if [[ "$COPILOT_ENVIRONMENT_NAME" == "dev" ]]; then
   ddtrace-run celery -A config worker -l DEBUG
else
   celery -A config worker -l DEBUG
fi
