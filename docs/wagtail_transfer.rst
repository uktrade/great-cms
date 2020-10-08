Wagtail Transfer
================

Status: DRAFT

We use ``Wagtail Transfer<https://wagtail.github.io/wagtail-transfer/>``_ to move content between (allowed) environments.

This work is currently IN PROGRESS


What does it do?
----------------

W-T allows a Wagtail site to import content FROM another site into itself, creating or updating pages as appropriate.

Think of is as one site pulling content from another.

As such, we need to carefully control which site can import data from which other site.

For now, the configuration provided by ``config.utils.get_wagtail_transfer_configuration()`` permits the following:

1. Import from Staging into Beta (so Beta needs to know about Staging)
2. Import from Beta into Staging (so Staging needs to know about Beta)
3. Import from Beta OR Staging into Dev (so Dev needs to know about both)
4. Local dev: only if enabled, a special setup for copying between two
    local runservers on different ports - see below for more info on how to set this up.

In the future, we may need to add configuration for UAT and/or Production
environments.


What doesn't it do?
-------------------

Currently, Wagtail Transfer does not:

* handle the moving of large files between systems without the risk of exceeding a 30-second timeout (for us on Gov UK PaaS).
* automatically reflect the deletion or movemement of pages on a source site. Support can be added, but needs further implementation work. For now we have a manual workaround.
* automatically handle the transfer of large media files that are featured in pages. This is more about the request timeout threshold of the platform we're on than W-T itself. Again, we can manually work around this.

There are workarounds documented in Confluence for all of the above.


GOTCHAS for developers
----------------------

1. When you add an entirely new model to the codebase, if it is featured in a Page (eg a new type of embedded media like a slide deck, or some other non-Wagtail model), you need to add it to `settings.WAGTAILTRANSFER_UPDATE_RELATED_MODELS` so that WT knows about it. You must ALSO test it with WT locally.

2. Pages/new objects added via data migrations may break WT - if you add a data migration, you need to test locally to be sure WT is happy with it, too.

3. When importing more than one new page, the primary keys of those pages can't be guaranteed to be the same as on the source site, so do not write any code that relies on a PK.

4. Pages that are fail to validate on save will NOT be transferred by WT - so if a Page type is updated with a new, required/non-null field but the Page lacks the data, that will BLOCK Wagtail Transfer from transferring that page.

5. If you want to test that WT will move your data without problem you will need to set up two local instances - docs are below

6. The Created and Modified timestamps that come from django-extensions are _overwritten_ at the destination side when WT saves an imported Page/Snippet.

7. The History section of Wagtail is no longer reliable once WT has been used, because it does not sync page-editing history.


Local setup if you need to develop against or test-drive W-T (eg with new content types)
----------------------------------------------------------------------------------------

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
