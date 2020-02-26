ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

ENV_FILES?='test,dev'
pytest:
	ENV_FILES=$(ENV_FILES) \
	pytest tests $(ARGUMENTS)

flake8:
	flake8 . \
	--exclude=.venv,venv,node_modules,migrations \
	--max-line-length=120

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)

ENV_FILES?='secrets-do-not-commit,dev'
check_migrations:
	yes n | ENV_FILES=$(ENV_FILES) ./manage.py migrate --plan

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver_plus 0.0.0.0:8020 $(ARGUMENTS)

LOCUST := \
	locust \
		--locustfile $$LOCUST_FILE \
		--clients=$$NUM_CLIENTS \
		--hatch-rate=$$HATCH_RATE \
		--only-summary \
		--no-web \
		--csv=./results/results \
		--run-time=$$RUN_TIME

kill_webserver := \
	pkill -f runserver_plus

test_load:
	ENV_FILES='test,dev' python manage.py runserver_plus 0.0.0.0:8020 &
	sleep 5
	$(LOCUST)
	-$(kill_webserver)

requirements:
	pip-compile -r --annotate requirements.in
	pip-compile -r --annotate requirements_test.in

install_requirements:
	pip install -q -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

secrets:
	cp config/env/secrets-template config/env/secrets-do-not-commit; \
	sed -i -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' config/env/secrets-do-not-commit

database:
	PGPASSWORD=debug dropdb -h localhost -U debug greatcms
	PGPASSWORD=debug createdb -h localhost -U debug greatcms


.PHONY: clean pytest test_load dflake8 manage webserver requirements install_requirements css worker secrets check_migrations database
