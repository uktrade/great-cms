# Great CMS

[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![docs-image]][docs]
[![gitflow-image]][gitflow]
[![semver-image]][semver]

**CMS for the GREAT platform - The Department for Business and Trade (DBT)**

---

## Development

### Installing

    $ git clone https://github.com/uktrade/great-cms
    $ cd great-cms
    $ [create and activate virtual environment]
    $ make install_requirements
    $ make secrets
    $ make ARGUMENTS=migrate manage

### Requirements

* [Python 3.9](https://www.python.org/downloads/release/python-3913/)
* [Postgres 10](https://www.postgresql.org/)
* [Redis](https://redis.io/)
* Any [browser based on Chromium](https://en.wikipedia.org/wiki/Chromium_(web_browser)#Browsers_based_on_Chromium)
  and [Chrome driver](https://chromedriver.chromium.org/)

### Install virtualenv.

`pip` is required. Refer to the [pip website](https://pip.pypa.io/en/stable/getting-started/) for more info.

### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/env/secrets-do-not-commit` - a file
that is not added to version control. To create a template secrets file with dummy values run `make secrets`.

### Commands

| Command                       | Description |
| ----------------------------- | ------------|
| make clean                    | Delete pyc files |
| make pytest                   | Run all tests |
| make pytest test_foo.py       | Run all tests in file called test_foo.py |
| make pytest -- --last-failed` | Run the last tests to fail |
| make pytest -- -k foo         | Run the test called foo |
| make pytest -- <foo>          | Run arbitrary pytest command |
| make test_load                | Run load tests |
| make flake8                   | Run flake8 linting only |
| make checks                   | Run black, isort and flake8 in check mode |
| make autoformat               | Run black and isort in file-editing mode |
| make manage <foo>             | Run arbitrary management command |
| make webserver                | Run the development web server |
| make requirements             | Compile the requirements file |
| make install_requirements     | Installed the compile requirements file |
| make css                      | Compile scss to css |
| make secrets                  | Create your secret env var file |

### Setting up the local database

    $ make database

`make database` drops then recreates the local database.

When setting up the project initially ensure you have postgress app running and have created a db called `greatcms` with
a user called `debug`. Instructions shown here

- https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e

Elevate user debug to superuser `ALTER USER debug WITH SUPERUSER;`

### Setting up the Chrome Driver

1. Download `Chrome driver` from the official site https://chromedriver.chromium.org/
2. Place the binary on you `PATH`

#### Running browser tests in "headfull" mode

In case you'd like to run all browser tests in "headfull" mode, then simply set `HEADLESS` env var to `false`:

```bash
HEADLESS=false make ARGUMENTS="-m browser" pytest
```

You can also use regular pytest filters:

```bash
HEADLESS=false make ARGUMENTS="-k test_anonymous_user_should" pytest
```

## Geolocation data

This project includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com/

Maxmind GeoLite2 is used to determine the city or country the user is from via their IP address. The geolocation dataset
must be updated to stay fresh. To pull a fresh version of the geolocation data, ensure you have MAXMIND_LICENCE_KEY set
to a valid key, then run:

```
make manage download_geolocation_data
```

and then delete the downloaded, unexpanded archives (*.gz) before commiting the changed *.mmdb files.

### Wagtail Transfer

We use a third-party app to manage content import from one environment to another. There are specific docs on Wagtail
Transer :doc:`here <./wagtail_transfer>`. PLEASE at last read the "GOTCHAS for developers"

### Image storage

Local development uses `django.core.files.storage.FileSystemStorage`, but you will be well advised to enable S3 storage
if you are testing/using Wagtail Transfer

### /etc/hosts file entry

UI clients on local expect the CMS to be reachable at the address http://greatcms.trade.great. Add the following to
your `/etc/hosts` file:

```
127.0.0.1   greatcms.trade.great
```

You can test this works by attempting to visit http://greatcms.trade.great:8020/admin in your browser.

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial
data in the session, because the browser will be exposed to the data.

## React components

To add new React components:

1. Add the file to javascript/src/ e.g. javascript/src/myFile.js
2. Update javascript/src/bundle.js e.g,

```
import myFile from './myFile';

export default {
    ...,
    myFile
};
```

3. Run `npm run build`
4. The new component is now available on window.magna.myFile

### Node version

Make sure to use NodeJS 14.0.0.

### Code formatting

We are using eslint with recommended settings

### Pre-commit hooks

Highly recommended that you install pre-commit hooks. you can take advantage of pre-commit to autoformat and lint/check
any code that's staged for commit

To get set up, in your activated virtualenv:

`pip install pre-commit`
`pre-commit install --install-hooks`

## FE Development

### Helpful links

* [Frontend how to guide](https://uktrade.atlassian.net/wiki/spaces/ED/pages/3544940573/Frontend+Development+on+great.gov.uk)


### JS and CSS builds

Most front-end assets are compiled from a single webpack configuration in `react-components/webpack.config.js`. This
compiles:

- The main JS bundle for Magna/Logged in
- The CSS styles for Magna/Logged in
- The CSS styles for Profile
- Some CSS for 'element components'
- The JS for the cookie banner

To compile all the above, run the default build script:

```shell
$ npm run build
```

There are other CSS files which are not covered by the above Webpack config, which are found in `domestic/sass`. To
compile those, run the domestic build script:

```shell
$ npm run build-domestic
```

### Development builds

The above scripts are available as development-focused watch tasks, and result in development versions of the above
assets:

```shell
$ npm run build:dev
$ npm run build-domestic:dev
```

NOTE: Make sure you run the production builds (not `:dev`) before committing work.

### JS tests

JS tests can be run with:

```shell
$ npm run test
```

Or as a watch task using:

```shell
$ npm run test:dev
```

## Staff SSO

On local machine, SSO is turned off by default. If you need to enable, set the `ENFORCE_STAFF_SSO_ENABLED` to `true`.
You also need to set:

```
STAFF_SSO_AUTHBROKER_URL
AUTHBROKER_CLIENT_ID
AUTHBROKER_CLIENT_SECRET
```

Speak to webops or a team mate for the above values.

## Load tests

We're using [locust](https://locust.io/) to run load tests against local instance of the service and in-memory SQLite.
See Django [database documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#databases) for more details.

To run them with default settings use:

```bash
make test_load
```

This target, will spawn a local instance of the service and tear it down after tests are finished.

You can control the execution with env vars:

```bash
LOCUST_FILE=tests/load/mvp_home.py NUM_USERS=10 HATCH_RATE=2 RUN_TIME=30s make test_load
```

## Known issues

* Local development environment: If you try to get to a URL (i.e. /export-plan/dashboard/) and you get an error similar
  to "AttributeError

AttributeError: 'User' object has no attribute 'session_id'"/'company' et al, you need to go to /django-admin/ and
logout from the top right hand side. This is a temporary workaround to resolve an incompatibility between great-cms and
directory-sso.

* On ubuntu you may need to run `sudo apt-get install libpq-dev` if after trying to install dependencies you get an
  error message relating to `psycopg`.

* On latest release of MacOs `make install_requirements` might fail, please run `brew install openssl`
  then `env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" make install_requirements`

___

## Docker setup

To setup and start Great CMS to run entirely in docker containers, use:

```
./start-docker.sh
```

This will clone required repositories (directory-api, directory-forms-api, directory-sso and directory-sso-proxy) into
the parent directory, and build the required containers.

During the process you will be asked to populate some environment variables: contact a team member to get the
appropriate values.

You will also need to add the following entries to your hosts file (/etc/hosts):

```
127.0.0.1       greatcms.trade.great
127.0.0.1       buyer.trade.great
127.0.0.1       supplier.trade.great
127.0.0.1       sso.trade.great
127.0.0.1       sso.proxy.trade.great
127.0.0.1       api.trade.great
127.0.0.1       profile.trade.great
```

The site will then be available at http://greatcms.trade.great:8020.

When the above setup has already been run, Great CMS can be started again with:

```
docker-compose -f development.yml up
```

___

## Helpful links

* [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist) # /PS-IGNORE
* [Gitflow branching](https://uktrade.atlassian.net/wiki/spaces/ED/pages/737182153/Gitflow+and+releases)
* [GDS service standards](https://www.gov.uk/service-manual/service-standard)
* [GDS design principles](https://www.gov.uk/design-principles)
* [Github Hooks](https://pre-commit.com/hooks)

## Related projects:

https://github.com/uktrade?q=directory

https://github.com/uktrade?q=great

[circle-ci-image]: https://circleci.com/gh/uktrade/great-cms/tree/develop.svg?style=svg

[circle-ci]: https://circleci.com/gh/uktrade/great-cms/tree/develop

[codecov-image]: https://codecov.io/gh/uktrade/great-cms/branch/master/graph/badge.svg

[codecov]: https://codecov.io/gh/uktrade/great-cms

[docs-image]: https://readthedocs.org/projects/great-cms/badge/?version=latest

[docs]: https://great-cms.readthedocs.io/en/latest/?badge=latest

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg

[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[semver-image]: https://img.shields.io/badge/Versioning%20strategy-SemVer-5FBB1C.svg

[semver]: https://semver.org
