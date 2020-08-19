# Great CM

[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![docs-image]][docs]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

**CMS for the GREAT platform - the Department for International Trade (DIT)**

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

* [Python 3.6](https://www.python.org/downloads/release/python-368/)
* [Postgres 10](https://www.postgresql.org/)
* [Redis](https://redis.io/)
* Any [browser based on Chromium](https://en.wikipedia.org/wiki/Chromium_(web_browser)#Browsers_based_on_Chromium) and [Chrome driver](https://chromedriver.chromium.org/)

### Install virtualenv

`pip` 18 is required. Refer to the [pip website](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py) for more info.

    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $ python get-pip.py pip==18

### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/env/secrets-do-not-commit` - a file that is not added to version control. To create a template secrets file with dummy values run `make secrets`.

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
| make flake8                   | Run linting |
| make manage <foo>             | Run arbitrary management command |
| make webserver                | Run the development web server |
| make requirements             | Compile the requirements file |
| make install_requirements     | Installed the compile requirements file |
| make css                      | Compile scss to css |
| make secrets                  | Create your secret env var file |
| make recreate                 | Runs following command in one go |
|                               | **make database**: Drop and recrete the database |
|                               | **make bootstrap_great**: Create required database records so the CMS works |
|                               | **make create_tours** |

### Setting up the local database

    $ make database

`make database` drops then recreates the local database.

When setting up the project initially ensure you have postgress app running and have created a db called `greatcms` with a user called `debug`. Instructions shown here - https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e

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


### Getting started

    $ make ARGUMENTS=bootstrap_great manage

 It creates the Great domestic empty homepage and assigns it to the site root.
 It also creates a superuser `test` with password `password`, for local development.


### Image storage

Local development uses `django.core.files.storage.FileSystemStorage`

### /etc/hosts file entry

UI clients on local expect the CMS to be reachable at the address http://cms.trade.great.

     Add 127.0.0.1 greatcms.trade.great

You can test this works by attempting to visit http://greatcms.trade.great:8020/admin in your browser.

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.

## React components

To add new react components:

1. Add the file to javascript/src/ e.g. javascript/src/myFile.js
2. Update javascript/src/bundle.js  e.g,
```
import myFile from './myFile';

export default {
    ...,
    myFile
};
```

3. Run `npm run build`
4. The new component is now available on window.ditMVP.myFile

### Node version
Make sure to use NodeJS 12.16.1 or greater

### Code formatting
We are using eslint with recommended settings and prettier

Are you using Visual Studio Code? Install Prettier plugin for auto formatting of your code:
https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode

## Staff SSO

On local machine, SSO is turned off by default.
If you need to enable, set the `FEATURE_ENFORCE_STAFF_SSO_ENABLED` to `true`.
You also need to set:
```
STAFF_SSO_AUTHBROKER_URL
AUTHBROKER_CLIENT_ID
AUTHBROKER_CLIENT_SECRET
```

Speak to webops or a team mate for the above values.


## Load tests

We're using [locust](https://locust.io/) to run load tests against local instance of
the service and in-memory SQLite.  
See Django [database documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#databases) for more details.

To run them with default settings use:
```bash
make test_load
```
This target, will spawn a local instance of the service and tear it down after tests
are finished.


You can control the execution with env vars:
```bash
LOCUST_FILE=tests/load/mvp_home.py NUM_USERS=10 HATCH_RATE=2 RUN_TIME=30s make test_load
```

## Known issues
* Local development environment: If you try to get to a URL (i.e. /markets/) and you get an error similar to "AttributeError

AttributeError: 'User' object has no attribute 'session_id'"/'company' et al, you need to go to /django-admin/ and logout from the top right hand side. This is a temporary workaround to resolve an incompatibility between great-cms and directory-sso.

* On ubuntu you may need to run `sudo apt-get install libpq-dev` if after trying to install dependencies you get an error message relating to `psycopg`.

## Helpful links
* [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)
* [Gitflow branching](https://uktrade.atlassian.net/wiki/spaces/ED/pages/737182153/Gitflow+and+releases)
* [GDS service standards](https://www.gov.uk/service-manual/service-standard)
* [GDS design principles](https://www.gov.uk/design-principles)


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

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org
