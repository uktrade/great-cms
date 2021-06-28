#!/bin/bash
set -e

# Fetch database file from s3 to restore
/data_dumps/getS3DataDump.sh

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER debug WITH PASSWORD 'debug';

    CREATE DATABASE directory_api_debug;
    CREATE DATABASE directory_sso_debug;
    CREATE DATABASE directory_forms_api_debug;
    CREATE DATABASE greatcms;


    GRANT ALL PRIVILEGES ON DATABASE directory_api_debug TO debug;
    GRANT ALL PRIVILEGES ON DATABASE directory_forms_api_debug TO debug;
    GRANT ALL PRIVILEGES ON DATABASE greatcms TO debug;
    GRANT ALL PRIVILEGES ON DATABASE directory_sso_debug TO debug;



EOSQL
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" greatcms < /data_dumps/$DATABASE_DUMP_FILENAME
