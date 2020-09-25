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
* The Makefile has been updated to include versions of common commands that use the special env file.
    * ``manage_transfer_target`` -- run management commands for the Transfer Target site
    * ``webserver_transfer_target`` -- run the web server for it, on 8030
    * ``database_transfer_target`` -- recreate the DB for the Transfer Target. More on this one below. There is not support for ``make recreate`` - you can do that by hand if you need it.




Local database setup
--------------------

1. Set up a local DB for the Transfer Target site

``make database_transfer_target``

2. Generate a dump of your local, standard, setup to load into the transfer target:

``pg_dump -U debug greatcms > /path/to/backup.sql``

3. Load the backup it in to your transfer-target database (``greatcms_transfer_target``) after you've made that DB:

``psql -U debug -d greatcms_transfer_target < path/to/backup.sql``
