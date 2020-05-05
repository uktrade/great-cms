Getting Started
===============


Exporting & Importing Wagtail DB
--------------------------------

This process was testes with following databases:

* source DB - Postgres v10 (Staging DB)
* target DB - Postgres v11.7 (local instance)

**Important note:**

Media files are not imported as they're stored in an external storage (S3).
It means that all videos, images, thumbnails, etc added via Wagtail admin wont'
show up after the import process is done.



1. Install `conduit` plugin for CloudFoundry
............................................

    .. code-block:: bash

        cf install-plugin conduit


2. Identify DB host
...................


    .. code-block:: bash

        cf s


3. Create a DB dump
...................


    .. code-block:: bash

        cf conduit <DB_HOSTNAME> -- pg_dump \
            --no-owner \
            --no-privileges \
            --no-owner \
            --file $(date --iso-8601)-wagtail_dump_no_owner.sql


4. Comment out redundant commands
.................................

    There are 2 things that needs to be commented out in the sql file:

    1. The whole `CREATE FUNCTION public.reassign_owned()` section

        This includes 2 `SET` commands that follow that function.
        This section is close to the beginning of the file:

        .. code-block:: sql

            CREATE FUNCTION public.reassign_owned() RETURNS event_trigger
                ...
            end
            $$;

            SET default_tablespace = '';

            SET default_with_oids = false;


    2. The last command in the sql file

        .. code-block:: sql

            CREATE EVENT TRIGGER reassign_owned ON ddl_command_end
                EXECUTE PROCEDURE public.reassign_owned();


5. Delete old greatcms DB and create an empty one
.................................................

        .. code-block:: bash

            make database


6. Import the data
..................

    .. code-block:: bash

        psql -U debug greatcms < $(date --iso-8601)-wagtail_dump_no_owner.sql


7. Run migrations
.................

    .. code-block:: bash

        make ARGUMENTS=migrate manage


8. Start the webserver
......................

    .. code-block:: bash

        make webserver
