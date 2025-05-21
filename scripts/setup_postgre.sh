#!/bin/bash

export $(grep -v '^#' .env | xargs)

DB_USER=$DB_USER
DB_PASS=$DB_PASSWORD
DB_NAME=$DB_NAME

sudo -u postgres psql <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_user
      WHERE  usename = '${DB_USER}') THEN

      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
   END IF;
END
\$do\$;

-- Creates the bank if it does not exist
CREATE DATABASE ${DB_NAME}
    WITH OWNER = ${DB_USER}
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE = template0;

-- Give all permissions in the database to the user
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- Grant permission to create databases (required for Django testing)
ALTER USER ${DB_USER} CREATEDB;
EOF

echo "User, database and permissions created/updated successfully."
