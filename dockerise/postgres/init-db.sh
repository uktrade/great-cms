#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE debug WITH LOGIN SUPERUSER PASSWORD 'debug';

    CREATE DATABASE directory_api_debug;
    CREATE DATABASE sso_debug;
    CREATE DATABASE directory_forms_api_debug;
    CREATE DATABASE greatcms;
EOSQL

# Fetch and load database file from S3
/data_dumps/getS3DataDump.sh
psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" greatcms < /data_dumps/$DATABASE_DUMP_FILENAME
