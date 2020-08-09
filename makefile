ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete
	-rm -fr ./allure_report/
	-rm -fr ./allure_results/

ENV_FILES?='test,dev'
pytest:
	ENV_FILES=$(ENV_FILES) \
	pytest \
		tests/unit \
		--junit-xml=./results/pytest_unit_report.xml \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov=. \
		$(ARGUMENTS)

# Usage: make pytest_single <path_to_file>::<method_name>
pytest_single:
	ENV_FILES=$(ENV_FILES) \
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
		--alluredir=./allure_results/ \
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

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver_plus 0.0.0.0:8020 $(ARGUMENTS)

LOCUST_FILE?=tests/load/mvp_home.py
NUM_USERS?=10
HATCH_RATE?=2
RUN_TIME?=30s
LOCUST := \
	locust \
		--locustfile $(LOCUST_FILE) \
		--users=$(NUM_USERS) \
		--hatch-rate=$(HATCH_RATE) \
		--run-time=$(RUN_TIME) \
		--headless \
		--csv=./results/results

kill_webserver := \
	pkill -f runserver_plus

test_load:
	ENV_FILES='test,dev' python manage.py runserver_plus 0.0.0.0:8020 &
	sleep 5
	$(LOCUST)
	-$(kill_webserver)

requirements:
	pip-compile --upgrade -r --annotate requirements.in
	pip-compile --upgrade -r --annotate requirements_test.in

install_requirements:
	pip install -q -r requirements_test.txt

secrets:
	cp config/env/secrets-template config/env/secrets-do-not-commit; \
	sed -i -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' config/env/secrets-do-not-commit

database:
	PGPASSWORD=debug dropdb --if-exists -h localhost -U debug greatcms
	PGPASSWORD=debug createdb -h localhost -U debug greatcms

recreate:
	$(MAKE) database
	$(MAKE) ARGUMENTS=migrate manage
	$(MAKE) ARGUMENTS=bootstrap_great manage
	$(MAKE) ARGUMENTS=create_tours manage

.PHONY: clean pytest test_load flake8 manage webserver requirements install_requirements css worker secrets check_migrations database recreate
