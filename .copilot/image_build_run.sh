#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied

# shellcheck disable=SC2046
export $(grep -v '^#' ./config/test | xargs)

echo "Running image_build_run.sh"

echo "Running collectstatic"
python manage.py collectstatic --noinput
