ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

# configuration for black and isort is in pyproject.toml
autoformat:
	isort $(PWD)
	black $(PWD)

checks:
	isort $(PWD) --check
	black $(PWD) --check --verbose
	flake8 .


ENV_FILES?='test,dev'
pytest:
	ENV_FILES=$(ENV_FILES) \
	DEBUG=False \
	pytest \
		tests/unit \
		--junit-xml=./results/pytest_unit_report.xml \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov=. \
		$(ARGUMENTS)

ENV_FILES?='test,dev'
pytest_codecov:
	ENV_FILES=$(ENV_FILES) \
	pytest \
		tests/unit \
		--junit-xml=./results/pytest_unit_report.xml \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov=. \
		--codecov \
		$(ARGUMENTS)

# Usage: make pytest_single <path_to_file>::<method_name>
pytest_single:
	ENV_FILES=$(ENV_FILES) \
	DEBUG=False \
	pytest \
	    $(ARGUMENTS)
		--junit-xml=./results/pytest_unit_report.xml \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov=. \

pytest_browser:
	ENV_FILES=$(ENV_FILES) \
	pytest \
		tests/browser \
		--junit-xml=./results/pytest_browser_report.xml \
		--ignore='./venv/' \
		--color=no \
		$(ARGUMENTS)

flake8:
	flake8 . \
	--exclude=ENV,ENV2,.venv,venv,node_modules,migrations \
	--max-line-length=120

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)


ENV_FILES?='secrets-do-not-commit,dev'
check_migrations:
	yes n | ENV_FILES=$(ENV_FILES) ./manage.py migrate --plan

webserver:  # runs on 8020
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver_plus 0.0.0.0:8020 --keep-meta-shutdown $(ARGUMENTS)

LOCUST_FILE?=tests/load/mvp_home.py
NUM_USERS?=10
HATCH_RATE?=2
RUN_TIME?=30s
LOCUST := \
	locust \
		--locustfile $(LOCUST_FILE) \
		--users=$(NUM_USERS) \
		--spawn-rate=$(HATCH_RATE) \
		--run-time=$(RUN_TIME) \
		--headless \
		--csv=./results/results

kill_webserver := \
	pkill -f runserver_plus

loadserver:  # runs on 8020
	ENV_FILES='test,dev' python manage.py runserver_plus 0.0.0.0:8020 --keep-meta-shutdown &

test_load:
	sleep 25
	$(LOCUST)
	-$(kill_webserver)

requirements:
	pip-compile --upgrade -r --annotate requirements.in
	pip-compile --upgrade -r --annotate requirements_test.in

install_requirements:
	pip install -q -r requirements_test.txt
	pre-commit install --install-hooks

secrets:
	@if [ ! -f ./config/env/secrets-do-not-commit ]; \
		then sed -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' config/env/secrets-template > config/env/secrets-do-not-commit \
			&& echo "Created config/env/secrets-do-not-commit"; \
		else echo "config/env/secrets-do-not-commit already exists. Delete first to recreate it."; \
	fi

database:
	PGPASSWORD=debug dropdb --if-exists -h localhost -U debug greatcms
	PGPASSWORD=debug createdb -h localhost -U debug greatcms

recreate:
	$(MAKE) database
	$(MAKE) ARGUMENTS=migrate manage
	$(MAKE) ARGUMENTS=bootstrap_great manage
	$(MAKE) ARGUMENTS=create_tours manage

worker:
	ENV_FILES='secrets-do-not-commit,dev' celery -A config worker -l info

beat:
	ENV_FILES='secrets-do-not-commit,dev' celery -A config beat -l info -S django


checkmigrations:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py makemigrations --dry-run --check


.PHONY: checkmigrations clean autoformat checks pytest test_load flake8 manage webserver requirements install_requirements css worker secrets check_migrations database recreate worker beat
