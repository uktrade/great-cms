# Great CMS

[![circle-ci-image]][circle-ci]
[![coverage-image]][coverage]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

**CMS for the GREAT platform - the Department for International Trade (DIT)**

---

## Development

### Installing
    $ git clone https://github.com/uktrade/directory-cms
    $ cd directory-cms
    $ [create and activate virtual environment]
    $ make install_requirements
    $ make manage migrate


### Requirements
[Python 3.6](https://www.python.org/downloads/release/python-368/)

[Postgres 9.5](https://www.postgresql.org/)

[Redis](https://redis.io/)

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
| make flake8                   | Run linting |
| make manage <foo>             | Run arbitrary management command |
| make webserver                | Run the development web server |
| make requirements             | Compile the requirements file |
| make install_requirements     | Installed the compile requirements file |
| make css                      | Compile scss to css |
| make secrets                  | Create your secret env var file |
| make database                 | Drop and recrete the database |

### Setting up the local database

    $ make database

`make database` drops then recreates the local database. 


### Image storage

Local development uses `django.core.files.storage.FileSystemStorage`

### /etc/hosts file entry

UI clients on local expect the CMS to be reachable at the address http://cms.trade.great.

     Add 127.0.0.1 greatcms.trade.great

You can test this works by attempting to visit http://greatcms.trade.great:8020/admin in your browser.

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.


## Caching



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

[coverage-image]: https://coveralls.io/repos/github/uktrade/great-cms/badge.svg
[coverage]: https://coveralls.io/github/uktrade/great-cms

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org
