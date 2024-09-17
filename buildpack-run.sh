#!/usr/bin/env bash
export NODE_HOME=/layers/paketo-buildpacks_node-engine/node

echo "Detecting Python installation method"

if [[ -d "/layers/paketo-buildpacks_pip-install" ]]; then
  echo "  Found paketo-buildpacks/pip-install buildpack, setting PYTHONPATH"
  export PYTHONPATH="$(cat /layers/paketo-buildpacks_pip-install/packages/env/PYTHONPATH.prepend):$PYTHONPATH"
fi

if [[ -d "/layers/paketo-buildpacks_pipenv-install" ]]; then
  echo "  Found paketo-buildpacks/pipenv-install buildpack, setting PYTHONPATH"
  if ls "$(cat /layers/paketo-buildpacks_pipenv-install/packages/env/PYTHONPATH.prepend)" 2> /dev/null; then
    export PYTHONPATH="$(cat /layers/paketo-buildpacks_pipenv-install/packages/env/PYTHONPATH.prepend):$PYTHONPATH"
  else
    echo "    PYTHONPATH not found in expected location because of the version of the pipenv buildpack in play. Adding the site-packages directory to the PYTHONPATH."
    PIPENV_WORKSPACE_DIR="$(ls /layers/paketo-buildpacks_pipenv-install/packages/ | grep workspace)"
    PYTHON_DIR="$(ls /layers/paketo-buildpacks_pipenv-install/packages/$PIPENV_WORKSPACE_DIR/lib/)"
    export PYTHONPATH="/layers/paketo-buildpacks_pipenv-install/packages/$PIPENV_WORKSPACE_DIR/lib/$PYTHON_DIR/site-packages:$PYTHONPATH"
  fi
fi

if [[ -d "/layers/paketo-buildpacks_poetry-install" ]]; then
  echo "  Found paketo-buildpacks/poetry-install buildpack, setting PYTHONPATH"
  export PYTHONPATH="$(cat /layers/paketo-buildpacks_poetry-install/poetry-venv/env/PYTHONPATH.prepend):$PYTHONPATH"
  export PATH="$(cat /layers/paketo-buildpacks_poetry-install/poetry-venv/env/PATH.prepend):$PATH"
fi

if [ -f "./.copilot/image_build_run.sh" ]; then
    bash ./.copilot/image_build_run.sh
fi
