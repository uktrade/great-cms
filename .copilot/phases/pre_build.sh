#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

if [ -f "./.gitmodules" ]; then
  echo ".gitmodules file exists. Modifying URLs..."
    account_id=$(echo $CODESTAR_CONNECTION_ARN | cut -d':' -f5)
    connection_id=$(echo $CODESTAR_CONNECTION_ARN | cut -d'/' -f2)
    git_clone_base_url="https://codestar-connections.eu-west-2.amazonaws.com/git-http/$account_id/eu-west-2/$connection_id/uktrade"

    git config --global credential.helper '!aws codecommit credential-helper $@'
    git config --global credential.UseHttpPath true

    sed -i "s|url = git@github.com:uktrade/\(.*\).git|url = $git_clone_base_url/\1.git|g" ./.gitmodules

    git submodule update --init --remote --recursive

else
  echo ".gitmodules file does not exist. No URLs to update."
fi

# Add commands below to run as part of the pre_build phase
