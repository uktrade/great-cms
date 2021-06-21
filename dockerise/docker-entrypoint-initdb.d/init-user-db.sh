#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER debug WITH PASSWORD 'debug';

    CREATE DATABASE directory_api_debug;
    CREATE DATABASE greatcms;
    CREATE DATABASE sso_debug;

    GRANT ALL PRIVILEGES ON DATABASE directory_api_debug TO debug;
    GRANT ALL PRIVILEGES ON DATABASE greatcms TO debug;
    GRANT ALL PRIVILEGES ON DATABASE sso_debug TO debug;
EOSQL
