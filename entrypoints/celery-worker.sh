#!/bin/bash

if [[ "$FEATURE_DATADOG" = true ]]; then
   ddtrace-run celery -A config worker -l DEBUG
else
   celery -A config worker -l DEBUG
fi