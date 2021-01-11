ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

pytest:
	ENV_FILES='test,dev' \
	pytest $(ARGUMENTS) \
	--ignore=node_modules \
	--capture=no \
	--nomigrations \
	--reuse-db \
	-Wignore::DeprecationWarning \
	-vv


flake8:
	flake8 . \
	--exclude=.venv,venv,.idea-env,setup.py,directory_components/version.py,node_modules \
	--max-line-length=120

manage:
	ENV_FILES='dev' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='dev' python manage.py runserver 0.0.0.0:9013 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -e .[test]; \
	pip install -e .[demo]; \
	pip install -e .[janitor]

css:
	./node_modules/.bin/gulp styles

publish:
	rm -rf build dist; \
	python setup.py bdist_wheel; \
	twine upload --username $$DIRECTORY_PYPI_USERNAME --password $$DIRECTORY_PYPI_PASSWORD dist/*

.PHONY: clean pytest flake8 manage webserver requirements install_requirements css publish
