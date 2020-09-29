Wagtail Transfer
================

Status: DRAFT

We use ``Wagtail Transfer<https://wagtail.github.io/wagtail-transfer/>``_ to move content between (allowed) environments.

This work is currently IN PROGRES


Local setup
-----------
You will need to set up set up a second local version of the site, so that you can transfer between them.

This second local site will be termed the 'Transfer Target', although moving content from it to the other
local site will also be possible.

* The default local site runs on 8020 - the Transfer Target will run on 8030.
* The Transfer Target uses the main settings.py BUT has a separate env file: ``config/env/dev-transfer-target``
* A separate Makefile has been added with versions of common commands that use the special env file. You need to reference it explicitly:

    * ``make --file=makefile-for-wagtail-transfer manage_transfer_target`` -- run management commands for the Transfer Target site, eg ``createsuperuser`` and ``migrate``
    * ``make --file=makefile-for-wagtail-transfer webserver_transfer_target`` -- run the web server for it, on 8030
    * ``make --file=makefile-for-wagtail-transfer database_transfer_target`` -- recreate the DB for the Transfer Target. More on this one below. There is not support for ``make recreate`` - you can do that by hand if you need it.

Note that using both sites (8020 and 8030) in different tabs in the same browser will cause frustration as you can only be logged in to one at a time. As such, it's recommended to use two separate browsers/containers/profiles


Local database setup
--------------------

1. Set up a local DB for the Transfer Target site

``make --file=makefile-for-wagtail-transfer database_transfer_target``

2. Generate a dump of your local, standard, setup to load into the transfer target:

``pg_dump -U debug greatcms > /path/to/backup.sql``

3. Load the backup it in to your transfer-target database (``greatcms_transfer_target``) after you've made that DB:

``psql -U debug -d greatcms_transfer_target < path/to/backup.sql``


AWS S3 Setup
------------
Wagtail Transfer will move files that are referenced by pages. As such, it is best to have your local
builds (both of them) configured to use S3 for media storage.

* in your secrets-do-not-commit, set:
    * ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` to values for a non-production account (eg dev)
    * ``DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage``
    * ``SECRET_KEY`` need to be set to some string, too, if not already set
    * ``WAGTAIL_TRANSFER_LOCAL_DEV`` to ``True``

For the account that matches the access key you specified accountm, created two buckets, if needed::

* great-local-bucket-one -- for the normal local site on 8020
* great-local-bucket-two -- for the transfer target site on 8030
