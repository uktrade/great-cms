#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied

# mkdir -p /tmp/core/geolocation_data
# cp -a ./core/geolocation_data/. /tmp/core/geolocation_data/
# echo "LIST CONTENTS OF GEOLOCATION"
# ls /tmp/core/geolocation_data
